"""Download and submission connectors for SDMX .Stat Suite services."""

from __future__ import annotations

import json
import re
import time
from enum import Enum
from io import BytesIO
from typing import (
    TYPE_CHECKING,
    Any,
    Literal,
    Mapping,
    NoReturn,
    Optional,
    Sequence,
    Union,
)

import httpx
from msgspec import Struct, structs

from pysdmx import errors
from pysdmx.api.fmr import (
    AsyncRegistryClient,
    DataflowDetails,
    RegistryClient,
)
from pysdmx.api.qb import (
    ApiVersion,
    AsyncRestService,
    DataContext,
    DataFormat,
    DataQuery,
    RestService,
    SchemaContext,
    StructureDetail,
    StructureFormat,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.io import get_datasets, read_sdmx
from pysdmx.io.format import Format
from pysdmx.io.writer import write_sdmx
from pysdmx.model import (
    AgencyScheme,
    Categorisation,
    CategoryScheme,
    Codelist,
    ConceptScheme,
    Dataflow,
    DataProviderScheme,
    DataStructureDefinition,
    Hierarchy,
    Metadataflow,
    MetadataProviderScheme,
    MetadataProvisionAgreement,
    MetadataStructure,
    MultiRepresentationMap,
    ProvisionAgreement,
    RepresentationMap,
    StructureMap,
    TransformationScheme,
)
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.dataset import ActionType, Dataset
from pysdmx.util import experimental, parse_short_urn
from pysdmx.util._net_utils import BearerAuth, map_httpx_errors

if TYPE_CHECKING:  # pragma: no cover
    from pysdmx.io.pd import PandasDataset
    from pysdmx.model import (
        Agency,
        DataflowInfo,
        DataProvider,
        MetadataReport,
        Schema,
    )


class SubmissionResult(Struct, frozen=True, repr_omit_defaults=True):
    """Outcome of a .Stat data submission or status poll.

    Attributes:
        success: Whether the operation succeeded.
        message: The service message (or raw body when not JSON).
        request_id: The async transaction id, when known.
        execution_status: The status poll's execution status, if any.
        outcome: The status poll's outcome, if any.
        logs: Any log lines returned by a status poll.
    """

    success: bool
    message: str = ""
    request_id: Optional[int] = None
    execution_status: Optional[str] = None
    outcome: Optional[str] = None
    logs: tuple[str, ...] = ()


class StructureSubmissionResult(Struct, frozen=True, repr_omit_defaults=True):
    """Outcome of a .Stat structure submission or deletion.

    Attributes:
        success: True when every reported artefact code is 200/201.
        messages: The per-artefact messages the service returned.
    """

    success: bool
    messages: tuple[str, ...] = ()


def _submission_from_import(text: str) -> SubmissionResult:
    """Parse a Transfer ``OperationResult`` (import/delete ack)."""
    try:
        payload = json.loads(text)
    except ValueError:
        return SubmissionResult(success=False, message=text.strip())
    data = payload if isinstance(payload, dict) else {}
    lower = {k.lower(): v for k, v in data.items()}
    message = str(lower.get("message") or "")
    rid = re.search(r"ID\s+(\d+)", message)
    return SubmissionResult(
        success=bool(lower.get("success", True)),
        message=message,
        request_id=int(rid.group(1)) if rid else lower.get("requestid"),
    )


def _submission_from_status(text: str) -> SubmissionResult:
    """Parse a Transfer ``ImportSummary`` (status poll)."""
    try:
        payload = json.loads(text)
    except ValueError:
        return SubmissionResult(success=False, message=text.strip())
    if not isinstance(payload, dict):
        return SubmissionResult(success=False, message=text.strip())
    lower = {k.lower(): v for k, v in payload.items()}
    outcome = lower.get("outcome")
    logs = tuple(
        str(e.get("message") or e) if isinstance(e, dict) else str(e)
        for e in (lower.get("logs") or [])
    )
    return SubmissionResult(
        success=outcome == "Success",
        message=str(outcome or lower.get("executionstatus") or ""),
        request_id=lower.get("requestid"),
        execution_status=lower.get("executionstatus"),
        outcome=outcome,
        logs=logs,
    )


def _structure_result(text: str) -> StructureSubmissionResult:
    """Parse an NSIWS ``SubmitStructureResponse`` error envelope."""
    pairs = re.findall(
        r'code="(\d+)"[^>]*>\s*<[^>]*Text[^>]*>(.*?)</', text, re.DOTALL
    )
    return StructureSubmissionResult(
        success=all(c in {"200", "201"} for c, _ in pairs),
        messages=tuple(t.strip() for _, t in pairs),
    )


class StatEndpoints(str, Enum):
    """Known .Stat Suite deployments.

    The first group are **verified** SDMX-REST v2 base URLs, ready to
    pass to :class:`StatConnector`. The second group are the
    deployments' Data Explorer (UI) URLs, listed for reference only --
    they are **not** confirmed SDMX-REST endpoints, so pass the actual
    REST base to :class:`StatConnector` if one of them does not resolve.
    """

    # Verified SDMX-REST v2 base URLs.
    OECD = "https://sdmx.oecd.org/public/rest/v2"
    ILO = "https://sdmx.ilo.org/rest/v2"
    ABS = "https://data.api.abs.gov.au/rest/v2"
    PACIFIC = "https://stats-sdmx-disseminate.pacificdata.org/rest/v2"
    STATEC = "https://lustat.statec.lu/rest/v2"
    SIMEL_SV = "https://disseminatesimel.mtps.gob.sv/rest/v2"

    # Other known deployments -- Data Explorer URLs, NOT confirmed
    # SDMX-REST bases (adjust to the deployment's REST endpoint before
    # use). Listed for reference.
    INE_CHILE = "https://de.ine.gob.cl/"
    CAMSTAT = "http://camstat.nis.gov.kh/"
    FAO = "https://de-public-statsuite.fao.org/"
    FCSC_UAE = "https://uaestat.fcsc.gov.ae/"
    NBB = "https://dataexplorer.nbb.be/"
    SNZ = "https://explore.data.stats.govt.nz/"
    MALDIVES = "https://data.statisticsmaldives.gov.mv/"
    MALTA = "https://statdb.nso.gov.mt/"
    THAI_NSO = "https://stathub.nso.go.th/"
    UNESCAP = "https://dataexplorer.unescap.org/"
    SIMEL_UY = "https://de-mtss.simel.mtss.gub.uy/"
    STATCAN_CCEI = "https://de-ccei.statcan.gc.ca/"
    STATCAN_CITH = "https://de-cith.statcan.gc.ca/"
    ELSTAT = "https://explore.statistics.gr/"
    SAMOA = "https://data.sbs.gov.ws/"
    FIJI = "https://data.statsfiji.gov.fj/"
    BOTSWANA_LMO = "https://de.lmis.hrdc.org.bw/"
    UGANDA_LMIS = "https://de.lmis.mglsd.go.ug/"
    SWISS_FSO = "https://stats.swiss/"


@experimental
class StatConnector(RegistryClient):
    """Read connector for .Stat Suite SDMX-REST v2 services.

    Inherits :class:`~pysdmx.api.fmr.RegistryClient`, so its ``get_*``
    methods return the same model objects -- but it reads .Stat's
    SDMX-ML 2.1 and parses it with :func:`~pysdmx.io.read_sdmx` (the FMR
    client's JSON deserializers do not apply). Structure types or
    endpoints .Stat does not serve raise :class:`~pysdmx.errors.Invalid`.

    Adds .Stat-specific data retrieval, which the FMR client does not
    offer: :meth:`fetch_data` (raw SDMX-CSV) and :meth:`fetch_dataset`
    (a typed ``PandasDataset``). Reads are anonymous.

    Obtain the ``agency``, ``id`` and ``version`` of a dataflow from the
    OECD Data Explorer (https://data-explorer.oecd.org) via its
    "Developer API" button.
    """

    def __init__(
        self,
        api_endpoint: str = StatEndpoints.OECD,
        pem: Optional[str] = None,
        timeout: float = 20.0,
    ) -> None:
        """Instantiate a .Stat Suite read connector.

        Args:
            api_endpoint: The SDMX-REST v2 entry point. Defaults to the
                OECD public service.
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
        """
        super().__init__(
            api_endpoint, StructureFormat.SDMX_JSON_2_0_0, pem, timeout
        )
        # .Stat serves SDMX-ML 2.1 structures + SDMX-CSV data; parse with
        # read_sdmx rather than the inherited (JSON) deserializers.
        self._svc = RestService(
            self.api_endpoint,
            ApiVersion.V2_0_0,
            data_format=DataFormat.SDMX_CSV_1_0_0,
            structure_format=StructureFormat.SDMX_ML_2_1,
            timeout=timeout,
            pem=pem,
        )

    def _structures(self, query: StructureQuery) -> Sequence[Any]:
        """Fetch a structure query and parse it into model artefacts."""
        raw = self._svc.structure(query)
        return read_sdmx(BytesIO(raw), validate=False).structures or ()

    def _one(self, query: StructureQuery, typ: Any) -> Any:
        for artefact in self._structures(query):
            if isinstance(artefact, typ):
                return artefact
        raise errors.NotFound(
            "Artefact not found",
            "The service returned no matching artefact.",
        )

    def _many(self, query: StructureQuery, typ: Any) -> Any:
        return [a for a in self._structures(query) if isinstance(a, typ)]

    @staticmethod
    def _unsupported(name: str) -> NoReturn:
        raise errors.Invalid(
            "Not available on .Stat",
            f"'{name}' is not served by .Stat Suite deployments.",
        )

    def get_agencies(self, agency: str) -> Sequence["Agency"]:
        """Get the sub-agencies for the supplied agency."""
        scheme = self._one(self._agencies_q(agency), AgencyScheme)
        return scheme.items

    def get_providers(
        self, agency: str, with_flows: bool = False
    ) -> Sequence["DataProvider"]:
        """Get the data providers for the supplied agency."""
        query = self._providers_q(agency, with_flows)
        return self._one(query, DataProviderScheme).items

    def get_metadata_providers(
        self, agency: str, with_flows: bool = False
    ) -> Sequence["DataProvider"]:
        """Get the metadata providers for the supplied agency."""
        query = self._metadata_providers_q(agency, with_flows)
        return self._one(query, MetadataProviderScheme).items

    def get_categories(
        self, agency: str, id: str, version: str = "~"
    ) -> CategoryScheme:
        """Get the category scheme matching the parameters."""
        query = self._categories_q(agency, id, version)
        return self._one(query, CategoryScheme)

    def get_categorisation(
        self, agency: str, id: str, version: str = "~"
    ) -> Categorisation:
        """Get the categorisation matching the parameters."""
        query = self._categorisation_q(agency, id, version)
        return self._one(query, Categorisation)

    def get_provision_agreement(
        self, agency: str, id: str, version: str = "~"
    ) -> ProvisionAgreement:
        """Get the provision agreement matching the parameters."""
        query = self._pa_q(agency, id, version)
        return self._one(query, ProvisionAgreement)

    def get_codes(self, agency: str, id: str, version: str = "~") -> Codelist:
        """Get the codelist matching the parameters."""
        return self._one(self._codes_cl_q(agency, id, version), Codelist)

    def get_concepts(
        self, agency: str, id: str, version: str = "~"
    ) -> ConceptScheme:
        """Get the concept scheme matching the parameters."""
        return self._one(self._concepts_q(agency, id, version), ConceptScheme)

    def get_schema(
        self,
        context: Union[
            SchemaContext,
            Literal["dataflow", "datastructure", "provisionagreement"],
        ],
        agency: str,
        id: str,
        version: str,
    ) -> "Schema":
        """Not served by .Stat (no SDMX-REST ``/schema`` endpoint)."""
        self._unsupported("get_schema")

    def get_dataflow_details(
        self,
        agency: str,
        id: str,
        version: str = "~",
        detail: Union[
            DataflowDetails,
            Literal["all", "core", "providers", "schema"],
        ] = DataflowDetails.ALL,
    ) -> "DataflowInfo":
        """Not served by .Stat."""
        self._unsupported("get_dataflow_details")

    def get_dataflows(
        self, agency: str = "*", id: str = "*", version: str = "~"
    ) -> Sequence[Dataflow]:
        """Get the dataflow(s) matching the parameters."""
        return self._many(self._dataflows_q(agency, id, version), Dataflow)

    def get_data_structures(
        self, agency: str = "*", id: str = "*", version: str = "~"
    ) -> Sequence[DataStructureDefinition]:
        """Get the data structure(s) matching the parameters."""
        query = self._data_structures_q(agency, id, version)
        return self._many(query, DataStructureDefinition)

    def get_hierarchy(
        self, agency: str, id: str, version: str = "~"
    ) -> Hierarchy:
        """Get the hierarchy matching the parameters."""
        return self._one(self._hierarchy_q(agency, id, version), Hierarchy)

    def get_report(
        self, provider: str, id: str, version: str = "~"
    ) -> "MetadataReport":
        """Not served by .Stat."""
        self._unsupported("get_report")

    def get_reports(
        self,
        artefact_type: str,
        agency: str,
        id: str,
        version: str = "~",
    ) -> Sequence["MetadataReport"]:
        """Not served by .Stat."""
        self._unsupported("get_reports")

    def get_metadata_structures(
        self, agency: str = "*", id: str = "*", version: str = "~"
    ) -> Sequence[MetadataStructure]:
        """Get the metadata structure(s) matching the parameters."""
        query = self._msds_q(agency, id, version)
        return self._many(query, MetadataStructure)

    def get_metadataflows(
        self, agency: str = "*", id: str = "*", version: str = "~"
    ) -> Sequence[Metadataflow]:
        """Get the metadataflow(s) matching the parameters."""
        query = self._metadataflows_q(agency, id, version)
        return self._many(query, Metadataflow)

    def get_metadata_provision_agreement(
        self, agency: str, id: str, version: str = "~"
    ) -> MetadataProvisionAgreement:
        """Get the metadata provision agreement matching the parameters."""
        query = self._mpa_q(agency, id, version)
        return self._one(query, MetadataProvisionAgreement)

    def get_mapping(
        self, agency: str, id: str, version: str = "~"
    ) -> StructureMap:
        """Get the structure map matching the parameters."""
        return self._one(self._mapping_q(agency, id, version), StructureMap)

    def get_code_map(
        self, agency: str, id: str, version: str = "~"
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Get the representation map matching the parameters."""
        query = self._code_map_q(agency, id, version)
        return self._one(query, (MultiRepresentationMap, RepresentationMap))

    def get_vtl_transformation_scheme(
        self, agency: str, id: str, version: str = "~"
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Get the VTL transformation scheme matching the parameters."""
        query = self._vtl_ts_q(agency, id, version)
        return self._one(query, TransformationScheme)

    def fetch_data(
        self, agency: str, id: str, version: str, key: str = "*"
    ) -> bytes:
        """Download the SDMX-CSV data for a dataflow.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.
            key: A positional series key (dimensions in data-structure
                order, ``.``-separated; ``*`` wildcards a dimension).
                Defaults to ``"*"`` (the whole dataflow).

        Returns:
            The raw SDMX-CSV data message.

        Raises:
            errors.NotFound: If no data is found.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        query = DataQuery(
            DataContext.DATAFLOW,
            agency,
            id,
            version,
            key=key,
            obs_dimension="AllDimensions",
        )
        return self._svc.data(query)

    def fetch_dataset(
        self, agency: str, id: str, version: str, key: str = "*"
    ) -> "PandasDataset":
        """Get data for a dataflow as a typed Pandas dataset.

        Downloads the dataflow's structure (with descendants) and its
        data, then combines them with pysdmx's native
        :func:`~pysdmx.io.get_datasets`, which attaches the schema.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.
            key: A positional series key (see :meth:`fetch_data`).

        Returns:
            The requested data as a ``PandasDataset`` with its schema.

        Raises:
            errors.NotFound: If no data or dataflow is returned.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        struct_query = StructureQuery(
            StructureType.DATAFLOW,
            agency,
            id,
            version,
            detail=StructureDetail.FULL,
            references=StructureReference.DESCENDANTS,
        )
        structure = self._svc.structure(struct_query)
        data = self.fetch_data(agency, id, version, key)
        datasets = get_datasets(
            BytesIO(data), BytesIO(structure), validate=False
        )
        return datasets[0]


@experimental
class StatAsyncConnector(AsyncRegistryClient):
    """Asynchronous read connector for .Stat Suite SDMX-REST v2 services.

    The async counterpart of :class:`StatConnector`: inherits
    :class:`~pysdmx.api.fmr.AsyncRegistryClient`, reads .Stat's SDMX-ML
    2.1 and parses it with :func:`~pysdmx.io.read_sdmx`, and raises
    :class:`~pysdmx.errors.Invalid` for endpoints .Stat does not serve.
    Adds async :meth:`fetch_data` and :meth:`fetch_dataset`.
    """

    def __init__(
        self,
        api_endpoint: str = StatEndpoints.OECD,
        pem: Optional[str] = None,
        timeout: float = 20.0,
    ) -> None:
        """Instantiate an async .Stat Suite read connector.

        Args:
            api_endpoint: The SDMX-REST v2 entry point. Defaults to the
                OECD public service.
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
        """
        super().__init__(
            api_endpoint, StructureFormat.SDMX_JSON_2_0_0, pem, timeout
        )
        self._svc = AsyncRestService(
            self.api_endpoint,
            ApiVersion.V2_0_0,
            data_format=DataFormat.SDMX_CSV_1_0_0,
            structure_format=StructureFormat.SDMX_ML_2_1,
            timeout=timeout,
            pem=pem,
        )

    async def _structures(self, query: StructureQuery) -> Sequence[Any]:
        """Fetch a structure query and parse it into model artefacts."""
        raw = await self._svc.structure(query)
        return read_sdmx(BytesIO(raw), validate=False).structures or ()

    async def _one(self, query: StructureQuery, typ: Any) -> Any:
        for artefact in await self._structures(query):
            if isinstance(artefact, typ):
                return artefact
        raise errors.NotFound(
            "Artefact not found",
            "The service returned no matching artefact.",
        )

    async def _many(self, query: StructureQuery, typ: Any) -> Any:
        found = await self._structures(query)
        return [a for a in found if isinstance(a, typ)]

    @staticmethod
    def _unsupported(name: str) -> NoReturn:
        raise errors.Invalid(
            "Not available on .Stat",
            f"'{name}' is not served by .Stat Suite deployments.",
        )

    async def get_agencies(self, agency: str) -> Sequence["Agency"]:
        """Get the sub-agencies for the supplied agency."""
        scheme = await self._one(self._agencies_q(agency), AgencyScheme)
        return scheme.items

    async def get_providers(
        self, agency: str, with_flows: bool = False
    ) -> Sequence["DataProvider"]:
        """Get the data providers for the supplied agency."""
        query = self._providers_q(agency, with_flows)
        scheme = await self._one(query, DataProviderScheme)
        return scheme.items

    async def get_metadata_providers(
        self, agency: str, with_flows: bool = False
    ) -> Sequence["DataProvider"]:
        """Get the metadata providers for the supplied agency."""
        query = self._metadata_providers_q(agency, with_flows)
        scheme = await self._one(query, MetadataProviderScheme)
        return scheme.items

    async def get_categories(
        self, agency: str, id: str, version: str = "~"
    ) -> CategoryScheme:
        """Get the category scheme matching the parameters."""
        query = self._categories_q(agency, id, version)
        return await self._one(query, CategoryScheme)

    async def get_categorisation(
        self, agency: str, id: str, version: str = "~"
    ) -> Categorisation:
        """Get the categorisation matching the parameters."""
        query = self._categorisation_q(agency, id, version)
        return await self._one(query, Categorisation)

    async def get_provision_agreement(
        self, agency: str, id: str, version: str = "~"
    ) -> ProvisionAgreement:
        """Get the provision agreement matching the parameters."""
        query = self._pa_q(agency, id, version)
        return await self._one(query, ProvisionAgreement)

    async def get_codes(
        self, agency: str, id: str, version: str = "~"
    ) -> Codelist:
        """Get the codelist matching the parameters."""
        query = self._codes_cl_q(agency, id, version)
        return await self._one(query, Codelist)

    async def get_concepts(
        self, agency: str, id: str, version: str = "~"
    ) -> ConceptScheme:
        """Get the concept scheme matching the parameters."""
        query = self._concepts_q(agency, id, version)
        return await self._one(query, ConceptScheme)

    async def get_schema(
        self,
        context: Union[
            SchemaContext,
            Literal["dataflow", "datastructure", "provisionagreement"],
        ],
        agency: str,
        id: str,
        version: str,
    ) -> "Schema":
        """Not served by .Stat (no SDMX-REST ``/schema`` endpoint)."""
        self._unsupported("get_schema")

    async def get_dataflow_details(
        self,
        agency: str,
        id: str,
        version: str = "~",
        detail: Union[
            DataflowDetails,
            Literal["all", "core", "providers", "schema"],
        ] = DataflowDetails.ALL,
    ) -> "DataflowInfo":
        """Not served by .Stat."""
        self._unsupported("get_dataflow_details")

    async def get_dataflows(
        self, agency: str = "*", id: str = "*", version: str = "~"
    ) -> Sequence[Dataflow]:
        """Get the dataflow(s) matching the parameters."""
        query = self._dataflows_q(agency, id, version)
        return await self._many(query, Dataflow)

    async def get_data_structures(
        self, agency: str = "*", id: str = "*", version: str = "~"
    ) -> Sequence[DataStructureDefinition]:
        """Get the data structure(s) matching the parameters."""
        query = self._data_structures_q(agency, id, version)
        return await self._many(query, DataStructureDefinition)

    async def get_hierarchy(
        self, agency: str, id: str, version: str = "~"
    ) -> Hierarchy:
        """Get the hierarchy matching the parameters."""
        query = self._hierarchy_q(agency, id, version)
        return await self._one(query, Hierarchy)

    async def get_report(
        self, provider: str, id: str, version: str = "~"
    ) -> "MetadataReport":
        """Not served by .Stat."""
        self._unsupported("get_report")

    async def get_reports(
        self,
        artefact_type: str,
        agency: str,
        id: str,
        version: str = "~",
    ) -> Sequence["MetadataReport"]:
        """Not served by .Stat."""
        self._unsupported("get_reports")

    async def get_metadata_structures(
        self, agency: str = "*", id: str = "*", version: str = "~"
    ) -> Sequence[MetadataStructure]:
        """Get the metadata structure(s) matching the parameters."""
        query = self._msds_q(agency, id, version)
        return await self._many(query, MetadataStructure)

    async def get_metadataflows(
        self, agency: str = "*", id: str = "*", version: str = "~"
    ) -> Sequence[Metadataflow]:
        """Get the metadataflow(s) matching the parameters."""
        query = self._metadataflows_q(agency, id, version)
        return await self._many(query, Metadataflow)

    async def get_metadata_provision_agreement(
        self, agency: str, id: str, version: str = "~"
    ) -> MetadataProvisionAgreement:
        """Get the metadata provision agreement matching the parameters."""
        query = self._mpa_q(agency, id, version)
        return await self._one(query, MetadataProvisionAgreement)

    async def get_mapping(
        self, agency: str, id: str, version: str = "~"
    ) -> StructureMap:
        """Get the structure map matching the parameters."""
        query = self._mapping_q(agency, id, version)
        return await self._one(query, StructureMap)

    async def get_code_map(
        self, agency: str, id: str, version: str = "~"
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Get the representation map matching the parameters."""
        query = self._code_map_q(agency, id, version)
        return await self._one(
            query, (MultiRepresentationMap, RepresentationMap)
        )

    async def get_vtl_transformation_scheme(
        self, agency: str, id: str, version: str = "~"
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Get the VTL transformation scheme matching the parameters."""
        query = self._vtl_ts_q(agency, id, version)
        return await self._one(query, TransformationScheme)

    async def fetch_data(
        self, agency: str, id: str, version: str, key: str = "*"
    ) -> bytes:
        """Download the SDMX-CSV data for a dataflow.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.
            key: A positional series key (dimensions in data-structure
                order, ``.``-separated; ``*`` wildcards a dimension).
                Defaults to ``"*"`` (the whole dataflow).

        Returns:
            The raw SDMX-CSV data message.

        Raises:
            errors.NotFound: If no data is found.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        query = DataQuery(
            DataContext.DATAFLOW,
            agency,
            id,
            version,
            key=key,
            obs_dimension="AllDimensions",
        )
        return await self._svc.data(query)

    async def fetch_dataset(
        self, agency: str, id: str, version: str, key: str = "*"
    ) -> "PandasDataset":
        """Get data for a dataflow as a typed Pandas dataset.

        Downloads the dataflow's structure (with descendants) and its
        data, then combines them with pysdmx's native
        :func:`~pysdmx.io.get_datasets`, which attaches the schema.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.
            key: A positional series key (see :meth:`fetch_data`).

        Returns:
            The requested data as a ``PandasDataset`` with its schema.

        Raises:
            errors.NotFound: If no data or dataflow is returned.
            errors.Invalid: If the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        struct_query = StructureQuery(
            StructureType.DATAFLOW,
            agency,
            id,
            version,
            detail=StructureDetail.FULL,
            references=StructureReference.DESCENDANTS,
        )
        structure = await self._svc.structure(struct_query)
        data = await self.fetch_data(agency, id, version, key)
        datasets = get_datasets(
            BytesIO(data), BytesIO(structure), validate=False
        )
        return datasets[0]


@experimental
class StatUploader:
    """Submit structures and data to a .Stat Suite service.

    .Stat Suite splits submission across two services. Structural
    metadata goes to the **NSI web service**
    (``POST {nsi}/rest/structure``, SDMX-ML 2.1). Data goes to the
    **Transfer service** as a ``multipart/form-data`` upload
    (``POST {transfer}/import/sdmxFile``, file field ``file``) scoped to
    a **data space**; it is asynchronous and returns a transaction id
    polled via ``POST {transfer}/status/request``. Both services require
    an OAuth2 / Keycloak bearer token. Payloads are built with pysdmx's
    :func:`pysdmx.io.write_sdmx`.

    The SDMX action (Append/Replace/Merge/Delete) is carried inside the
    submitted file (the SDMX-CSV 2.0 ``ACTION`` column, or the SDMX-ML
    dataset action), not as a request parameter. A dataflow's structure
    must exist before its data is loaded, so use :meth:`submit`
    (structure first, then data) for a new dataflow.

    This class is standalone (it does not inherit
    :class:`pysdmx.api.dc.rest.SdmxConnector`): submission needs
    authenticated ``POST`` requests, whereas the connector's
    ``RestService`` only performs anonymous ``GET`` requests.
    """

    def __init__(
        self,
        nsi_endpoint: str,
        transfer_endpoint: str,
        dataspace: Optional[str] = None,
        token: Optional[str] = None,
        pem: Optional[str] = None,
        timeout: Optional[float] = 60.0,
    ) -> None:
        """Instantiate a .Stat Suite submission connector.

        Args:
            nsi_endpoint: The NSI web service entry point used for
                structure submission (host of ``/rest/structure``).
            transfer_endpoint: The Transfer service entry point,
                INCLUDING the API-version segment, e.g.
                ``https://transfer-demo.siscc.org/3`` (the service
                versions its routes: ``/3/import/sdmxFile``,
                ``/3/status/request``).
            dataspace: The default .Stat data space that data submission
                and status polling target (e.g. ``"design"``). May be
                overridden per call; one of the two is required by those
                operations.
            token: An OAuth2 bearer token. Required for every submission
                and status call; obtain one via a flow in
                :mod:`pysdmx.api.stat.authentication` (e.g.
                ``KeycloakDeviceAuthentication(...).get_token()``).
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
        """
        self._nsi = nsi_endpoint.rstrip("/")
        self._transfer = transfer_endpoint.rstrip("/")
        self._dataspace = dataspace
        self._token = token
        self._ssl = (
            httpx.create_ssl_context(verify=pem)
            if pem
            else httpx.create_ssl_context()
        )
        self._timeout = timeout

    def _resolve_dataspace(self, dataspace: Optional[str]) -> str:
        """Return the per-call or default data space, or raise."""
        space = dataspace if dataspace is not None else self._dataspace
        if space is None:
            raise errors.Invalid(
                "Missing data space",
                "A data space is required for .Stat data submission and "
                "status polling. Pass dataspace=... to the method or the "
                "constructor.",
            )
        return space

    def _send(
        self,
        method: str,
        url: str,
        *,
        content: Optional[str] = None,
        content_type: Optional[str] = None,
        data: Optional[Mapping[str, str]] = None,
        files: Optional[Mapping[str, Any]] = None,
    ) -> httpx.Response:
        """Send an authenticated request; return the response.

        Each call uses one body style: a raw ``content`` body (with
        ``content_type``), or form ``data`` optionally combined with
        multipart ``files`` (the client sets the content type itself).

        Args:
            method: The HTTP method (``POST`` or ``GET``).
            url: The absolute request URL.
            content: An optional raw request body.
            content_type: The ``Content-Type`` for a raw ``content``
                body. Omit for form/multipart requests so the client can
                set it (with the multipart boundary).
            data: Optional form fields (URL-encoded, or multipart when
                combined with ``files``).
            files: Optional multipart file parts.

        Returns:
            The successful HTTP response.

        Raises:
            errors.Unauthorized: If no token was configured, or the
                service rejected it (HTTP 401/403).
            errors.Invalid: If the service returned another client error.
            errors.InternalError: If the service returned a server error.
            errors.Unavailable: If the service could not be reached.
        """
        if self._token is None:
            raise errors.Unauthorized(
                "Missing token",
                "A bearer token is required for .Stat submission "
                "operations. Pass token=..., e.g. obtained from a flow "
                "in pysdmx.api.stat.authentication.",
            )
        headers = {"Content-Type": content_type} if content_type else {}
        try:
            with httpx.Client(
                verify=self._ssl, follow_redirects=True
            ) as client:
                r = client.request(
                    method,
                    url,
                    content=content,
                    data=data,
                    files=files,
                    headers=headers,
                    auth=BearerAuth(self._token),
                    timeout=self._timeout,
                )
                if r.status_code in (401, 403):
                    raise errors.Unauthorized(
                        "Unauthorized",
                        f"The service rejected the token "
                        f"({r.status_code}). The request was `{url}`.",
                    )
                r.raise_for_status()
                return r
        except (httpx.RequestError, httpx.HTTPStatusError) as e:
            map_httpx_errors(e)

    def submit_structure(
        self,
        structures: Union[MaintainableArtefact, Sequence[Any]],
        structure_format: Format = Format.STRUCTURE_SDMX_JSON_2_0_0,
    ) -> StructureSubmissionResult:
        """Submit structural metadata to the NSI web service.

        The artefact(s) are serialized with :func:`write_sdmx` and posted
        to ``{nsi}/rest/structure``. The ``Content-Type`` is taken from
        ``structure_format``.

        Args:
            structures: A maintainable artefact (e.g. a ``Codelist`` or
                ``Dataflow``) or a sequence of maintainable artefacts.
            structure_format: The SDMX structure format to serialize to.
                Defaults to SDMX-JSON 2.0 -- the only format whose writer
                covers **every** SDMX artefact type (the SDMX-ML writers
                do not support the metadata artefacts and have narrower
                type coverage). Override with an SDMX-ML format
                (``STRUCTURE_SDMX_ML_2_1`` / ``3_0`` / ``3_1``) or
                ``STRUCTURE_SDMX_JSON_2_1_0`` for a deployment that
                requires it; :func:`write_sdmx` raises
                :class:`~pysdmx.errors.Invalid` for a type that the chosen
                format cannot serialize.

        Returns:
            A :class:`StructureSubmissionResult` parsed from the NSI
            ``SubmitStructureResponse`` body. A per-artefact failure
            surfaces as ``success=False`` (with the service messages),
            not as an exception: the service can report a failure inside
            the body even on an HTTP 200 response.

        Raises:
            errors.Invalid: If an artefact type cannot be serialized in
                ``structure_format``, or the service returns a client
                error.
            errors.Unauthorized: If the token is missing or rejected.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        body = write_sdmx(structures, structure_format)
        r = self._send(
            "POST",
            f"{self._nsi}/rest/structure",
            content=body,
            content_type=structure_format.value,
        )
        return _structure_result(r.text)

    def _import_data(
        self,
        dataset: Union[Dataset, Sequence[Dataset]],
        dataspace: Optional[str],
        data_format: Format,
    ) -> SubmissionResult:
        """Upload dataset(s) to the Transfer service (shared transport)."""
        space = self._resolve_dataspace(dataspace)
        body = write_sdmx(dataset, data_format) or ""
        # The Transfer file part must declare a plain content-type from
        # the service's whitelist (it auto-detects the SDMX format from
        # the bytes); the SDMX media types are rejected there.
        if "csv" in data_format.value:
            filename, file_ct = "data.csv", "text/csv"
        else:
            filename, file_ct = "data.xml", "text/xml"
        r = self._send(
            "POST",
            f"{self._transfer}/import/sdmxFile",
            data={"dataspace": space},
            files={"file": (filename, body, file_ct)},
        )
        return _submission_from_import(r.text)

    def submit_data(
        self,
        dataset: Union[Dataset, Sequence[Dataset]],
        dataspace: Optional[str] = None,
        data_format: Format = Format.DATA_SDMX_CSV_2_0_0,
    ) -> SubmissionResult:
        """Submit data to the Transfer service.

        The dataset is serialized with :func:`write_sdmx` and uploaded as
        a ``multipart/form-data`` request (file field ``file``, plus the
        required ``dataspace`` field) to ``{transfer}/import/sdmxFile``.
        The dataset must be Schema-backed (e.g. produced by
        ``StatConnector.fetch_dataset`` or ``pysdmx.io.get_datasets``); a
        dataset whose structure is a bare URN cannot be written. The
        per-row/per-dataset action is taken from the file (the SDMX-CSV
        2.0 ``ACTION`` column, or the SDMX-ML dataset action).

        Submission is asynchronous: the returned ``SubmissionResult``
        carries the transaction id (``request_id``) to pass to
        :meth:`submission_status`.

        Args:
            dataset: A Schema-backed dataset, or a sequence of them.
            dataspace: The target data space; defaults to the one set on
                the connector.
            data_format: The SDMX data format to serialize to -- an
                SDMX-CSV (``DATA_SDMX_CSV_1_0_0`` / ``2_0_0`` / ``2_1_0``)
                or SDMX-ML 2.1/3.0/3.1 data writer. Defaults to SDMX-CSV
                2.0; the Transfer service auto-detects the format.

        Returns:
            A :class:`SubmissionResult` with the acknowledgement
            ``success``, the service ``message``, and the ``request_id``
            (the async transaction id) to poll with
            :meth:`submission_status`.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If no data space is set, or the service
                returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        return self._import_data(dataset, dataspace, data_format)

    def delete_data(
        self,
        dataset: Union[Dataset, Sequence[Dataset]],
        dataspace: Optional[str] = None,
    ) -> SubmissionResult:
        """Delete data by submitting it with the SDMX Delete action.

        The dataset's observations are uploaded to the Transfer service
        as SDMX-CSV 2.0 with ``ACTION=D`` per row, which deletes the
        matching observations. Asynchronous, like :meth:`submit_data`.

        Args:
            dataset: A Schema-backed dataset (or a sequence of them)
                whose observations (keys) should be deleted.
            dataspace: The target data space; defaults to the one set on
                the connector.

        Returns:
            A :class:`SubmissionResult` with the acknowledgement
            ``success``, the service ``message``, and the ``request_id``
            (the async transaction id) to poll with
            :meth:`submission_status`.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If no data space is set, or the service
                returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        datasets = [dataset] if isinstance(dataset, Dataset) else list(dataset)
        marked = [
            structs.replace(d, action=ActionType.Delete) for d in datasets
        ]
        # Delete always uses SDMX-CSV 2.0 (the per-row ACTION column).
        return self._import_data(
            marked if len(marked) > 1 else marked[0],
            dataspace,
            Format.DATA_SDMX_CSV_2_0_0,
        )

    def delete_structure(
        self,
        artefacts: Union[
            MaintainableArtefact,
            str,
            Sequence[Union[MaintainableArtefact, str]],
        ],
    ) -> list[StructureSubmissionResult]:
        """Delete structural artefact(s) from the NSI web service.

        Each artefact is deleted with
        ``DELETE {nsi}/rest/{type}/{agency}/{id}/{version}`` (the type
        segment is the lower-cased SDMX type). Accepts a maintainable
        artefact, a short-URN string (e.g.
        ``"DataConstraint=MD:CR_A_DF(1.0)"``), or a sequence of either;
        a sequence is deleted **in order**, so pass dependents first.

        .Stat dependencies: a data import auto-creates an actual content
        constraint ``CR_A_<dataflow>``. To remove a dataflow, first
        :meth:`delete_data`, then delete that constraint, then the
        dataflow, its DSD and concept scheme (a wrong order yields a
        ``409``/:class:`~pysdmx.errors.Invalid`).

        Args:
            artefacts: The artefact(s) or short URN(s) to delete.

        Deletion is fail-fast: on the first error the exception is
        raised and an indeterminate prefix of the sequence may already
        have been deleted (re-run with the remaining artefacts). The NSI
        signals a delete failure with an HTTP status (mapped above)
        rather than an in-body error, but callers may still inspect the
        returned bodies.

        Returns:
            The parsed :class:`StructureSubmissionResult` for each
            artefact, in order.

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If the service returns a client error (e.g.
                a ``409`` because a dependent artefact still references
                it).
            errors.NotFound: If an artefact does not exist.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        items = (
            [artefacts]
            if isinstance(artefacts, (str, MaintainableArtefact))
            else list(artefacts)
        )
        responses = []
        for item in items:
            urn = item if isinstance(item, str) else item.short_urn
            try:
                ref = parse_short_urn(urn)
            except errors.Invalid as exc:
                raise errors.Invalid(
                    "Invalid artefact reference",
                    "Expected a short URN like 'Dataflow=MD:DF(1.0)'; "
                    f"got {urn!r}.",
                ) from exc
            url = (
                f"{self._nsi}/rest/{ref.sdmx_type.lower()}"
                f"/{ref.agency}/{ref.id}/{ref.version}"
            )
            responses.append(_structure_result(self._send("DELETE", url).text))
        return responses

    def submit(
        self,
        structures: Union[MaintainableArtefact, Sequence[Any]],
        dataset: Union[Dataset, Sequence[Dataset]],
        dataspace: Optional[str] = None,
    ) -> SubmissionResult:
        """Submit the structure(s) first, then the data.

        .Stat Suite requires a dataflow's structure to exist before its
        data can be loaded, so the structure is submitted synchronously
        and only then is the (asynchronous) data submission started.

        Args:
            structures: The structural metadata to submit first.
            dataset: The data to submit once the structure is in place.
            dataspace: The target data space for the data; defaults to
                the one set on the connector.

        Returns:
            The data submission's :class:`SubmissionResult` (with the
            ``request_id`` to poll with :meth:`submission_status`).

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If the structure submission was not
                successful (the data is then not submitted), if no data
                space is set, or the service returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        result = self.submit_structure(structures)
        if not result.success:
            raise errors.Invalid(
                "Structure submission failed",
                "The structure was not accepted, so the data was not "
                f"submitted: {'; '.join(result.messages)}",
            )
        return self.submit_data(dataset, dataspace=dataspace)

    def submission_status(
        self,
        request_id: str,
        dataspace: Optional[str] = None,
        *,
        wait: bool = False,
        interval: float = 3.0,
        attempts: int = 20,
    ) -> SubmissionResult:
        """Poll the status of an asynchronous data submission.

        Issues ``POST {transfer}/status/request`` with the ``dataspace``
        and ``id`` form fields.

        Args:
            request_id: The transaction id returned by :meth:`submit_data`
                or :meth:`submit`.
            dataspace: The data space the request was submitted to;
                defaults to the one set on the connector.
            wait: When True, poll until the ``execution_status`` is
                terminal (Completed/Failed/TimedOut/Canceled) or
                ``attempts`` is reached.
            interval: Seconds between polls when ``wait`` is True.
            attempts: Maximum number of polls when ``wait`` is True.

        Returns:
            The parsed :class:`SubmissionResult` (its ``execution_status``
            and ``outcome`` tell you whether the async job succeeded).

        Raises:
            errors.Unauthorized: If the token is missing or rejected.
            errors.Invalid: If no data space is set, or the service
                returns a client error.
            errors.InternalError: If the service returns a server error.
            errors.Unavailable: If the service cannot be reached.
        """
        space = self._resolve_dataspace(dataspace)
        terminal = {"Completed", "Failed", "TimedOut", "Canceled"}
        result = SubmissionResult(success=False)
        for _ in range(attempts if wait else 1):
            r = self._send(
                "POST",
                f"{self._transfer}/status/request",
                data={"dataspace": space, "id": request_id},
            )
            result = _submission_from_status(r.text)
            if not wait or result.execution_status in terminal:
                return result
            time.sleep(interval)
        return result


__all__ = [
    "StatAsyncConnector",
    "StatConnector",
    "StatEndpoints",
    "StatUploader",
    "StructureSubmissionResult",
    "SubmissionResult",
]
