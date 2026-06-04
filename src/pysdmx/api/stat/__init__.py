"""Download connector for SDMX .Stat Suite services (e.g. OECD)."""

from __future__ import annotations

from enum import Enum
from io import BytesIO
from typing import TYPE_CHECKING, Optional, Union

from msgspec import structs

from pysdmx import errors
from pysdmx.api.dc.query import BasicFilter
from pysdmx.api.dc.query.util import parse_query
from pysdmx.api.qb import (
    ApiVersion,
    DataContext,
    DataFormat,
    DataQuery,
    RestService,
    StructureDetail,
    StructureFormat,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.io import get_datasets, read_sdmx
from pysdmx.model import Dataflow, DataStructureDefinition, Schema
from pysdmx.model.message import Message
from pysdmx.util import experimental, parse_short_urn
from pysdmx.util._model_utils import schema_generator

if TYPE_CHECKING:  # pragma: no cover
    from pysdmx.io.pd import PandasDataset


class StatEndpoints(str, Enum):
    """Known .Stat Suite SDMX-REST v2 entry points.

    Each entry is verified to expose the SDMX-REST v2 API and to serve
    structural metadata as SDMX-ML 2.1.
    """

    OECD = "https://sdmx.oecd.org/public/rest/v2"
    ILO = "https://sdmx.ilo.org/rest/v2"
    ABS = "https://data.api.abs.gov.au/rest/v2"
    PACIFIC = "https://stats-sdmx-disseminate.pacificdata.org/rest/v2"


@experimental
class StatConnector:
    """Download connector for .Stat Suite SDMX-REST v2 services.

    .Stat Suite deployments (e.g. OECD dotStatSuite) serve structural
    metadata as SDMX-ML 2.1 and data as SDMX-CSV, and do not expose the
    SDMX-REST ``/schema`` endpoint. This connector retrieves a single
    SDMX-ML 2.1 structure message (with descendants) plus SDMX-CSV 1.0.0
    data, and relies on pysdmx's native readers to produce a ``Dataflow``,
    a ``Schema`` and a ``PandasDataset``.

    Obtain the ``agency``, ``id`` and ``version`` of a dataflow from the
    OECD Data Explorer (https://data-explorer.oecd.org) via its
    "Developer API" button.
    """

    def __init__(
        self,
        api_endpoint: Union[str, StatEndpoints] = StatEndpoints.OECD,
        pem: Optional[str] = None,
        timeout: Optional[float] = 20.0,
    ) -> None:
        """Instantiate a .Stat Suite download connector.

        Args:
            api_endpoint: The SDMX-REST v2 entry point. Defaults to the
                OECD public service.
            pem: Optional PEM file with trusted certificate authorities,
                for services using a self-signed certificate.
            timeout: Maximum number of seconds to wait per request.
        """
        self._svc = RestService(
            api_endpoint,
            ApiVersion.V2_0_0,
            data_format=DataFormat.SDMX_CSV_1_0_0,
            structure_format=StructureFormat.SDMX_ML_2_1,
            timeout=timeout,
            pem=pem,
        )

    def _fetch_structure(
        self, agency: str, id: str, version: str
    ) -> tuple[bytes, Message]:
        """Fetch the SDMX-ML 2.1 structure (with descendants)."""
        q = StructureQuery(
            StructureType.DATAFLOW,
            agency,
            id,
            version,
            detail=StructureDetail.FULL,
            references=StructureReference.DESCENDANTS,
        )
        raw = self._svc.structure(q)
        msg = read_sdmx(BytesIO(raw), validate=False)
        return raw, msg

    def _find_dataflow(
        self, msg: Message, agency: str, id: str, version: str
    ) -> Dataflow:
        """Return the Dataflow contained in a structure message."""
        for artefact in msg.structures or []:
            if isinstance(artefact, Dataflow) and artefact.id == id:
                return artefact
        raise errors.NotFound(
            "Dataflow not found",
            (
                f"No dataflow {agency}:{id}({version}) was returned by "
                "the service. Verify the agency, id and version."
            ),
        )

    def _find_dsd(self, msg: Message) -> DataStructureDefinition:
        """Return the data structure definition in a structure message."""
        for artefact in msg.structures or []:
            if isinstance(artefact, DataStructureDefinition):
                return artefact
        raise errors.NotFound(
            "Data structure not found",
            "The structure message did not include a data structure "
            "definition. Re-run the structure query with references.",
        )

    def dataflow(self, agency: str, id: str, version: str) -> Dataflow:
        """Get the dataflow matching the supplied identification.

        The dataflow's data structure definition is grafted onto the
        returned object so that ``Dataflow.components`` is populated; a
        plain parse leaves ``structure`` as a URN and ``components`` None.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.

        Returns:
            The dataflow, including its components (from the DSD).

        Raises:
            errors.NotFound: If the dataflow or its DSD is not returned.
            errors.Invalid: If the service returns a client error.
            errors.Unavailable: If the service cannot be reached.
        """
        _, msg = self._fetch_structure(agency, id, version)
        flow = self._find_dataflow(msg, agency, id, version)
        dsd = self._find_dsd(msg)
        return structs.replace(flow, structure=dsd)

    def schema(self, agency: str, id: str, version: str) -> Schema:
        """Get the data validity schema for a dataflow.

        The schema is derived from the dataflow's data structure
        definition, as .Stat Suite services do not expose the
        SDMX-REST ``/schema`` endpoint.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.

        Returns:
            The dataflow-context schema (components and their types).

        Raises:
            errors.NotFound: If the dataflow is not returned.
            errors.Invalid: If the service returns a client error.
            errors.Unavailable: If the service cannot be reached.
        """
        _, msg = self._fetch_structure(agency, id, version)
        flow = self._find_dataflow(msg, agency, id, version)
        return schema_generator(msg, parse_short_urn(flow.short_urn))

    def dataset(
        self,
        agency: str,
        id: str,
        version: str,
        key: str = "*",
        filters: Optional[Union[BasicFilter, str]] = None,
    ) -> "PandasDataset":
        """Get data for a dataflow as a typed Pandas dataset.

        The data are retrieved as SDMX-CSV 1.0.0 and combined with the
        dataflow's SDMX-ML 2.1 structure so the returned dataset carries
        a resolved ``Schema`` and PyArrow-backed column types.

        Args:
            agency: The agency maintaining the dataflow.
            id: The dataflow ID.
            version: The dataflow version.
            key: The dimension key identifying the slice of the cube
                (e.g. ``A.U.A.B.5J``). ``*`` (default) returns all series.
            filters: Optional component filters, as a string
                ("FREQ = 'A'") or a filter object from
                ``pysdmx.api.dc.query``.

        Returns:
            The requested data as a ``PandasDataset`` with its schema.

        Raises:
            errors.NotFound: If no data or dataflow is returned.
            errors.Invalid: If the service returns a client error.
            errors.Unavailable: If the service cannot be reached.
        """
        components = (
            parse_query(filters) if isinstance(filters, str) else filters
        )
        dq = DataQuery(
            DataContext.DATAFLOW,
            agency,
            id,
            version,
            key=key,
            components=components,  # type: ignore[arg-type]
            obs_dimension="AllDimensions",
        )
        data = self._svc.data(dq)
        raw_struct, _ = self._fetch_structure(agency, id, version)
        datasets = get_datasets(
            BytesIO(data), BytesIO(raw_struct), validate=False
        )
        return datasets[0]


__all__ = ["StatConnector", "StatEndpoints"]
