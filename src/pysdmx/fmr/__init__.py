"""Retrieve metadata from an FMR instance."""
from enum import Enum
from typing import Any, Literal, NoReturn, Optional, Sequence, Tuple, Union

import httpx
from msgspec.json import decode

from pysdmx.errors import ClientError, NotFound, ServiceError, Unavailable
from pysdmx.fmr.fusion import deserializers as fusion_deserializers
from pysdmx.fmr.reader import Deserializer
from pysdmx.fmr.sdmx import deserializers as sdmx_deserializers
from pysdmx.model import (
    CategoryScheme,
    Codelist,
    ConceptScheme,
    DataflowInfo,
    Hierarchy,
    MetadataReport,
    Organisation,
    Schema,
    StructureMap,
    ValueMap,
)


class Format(Enum):
    """The list of supported formats."""

    SDMX_JSON = "application/vnd.sdmx.structure+json;version=2.0.0"
    """The SDMX-JSON 2.0.0 Structure format."""
    FUSION_JSON = "application/vnd.fusion.json"
    """The proprietary Fusion-JSON format used internally by the FMR."""


class DataflowDetails(Enum):
    """The list of allowed details for dataflow queries."""

    ALL = "all"
    """All available information about a dataflow."""
    CORE = "core"
    """Core information about a dataflow (ID, name, description, etc.)."""
    PROVIDERS = "providers"
    """Core information about a dataflow and the list of providers."""
    SCHEMA = "schema"
    """Core information about a dataflow and its schema (data structure.)"""


class Context(Enum):
    """The context from which the schema is derived."""

    DATAFLOW = "dataflow"
    """DSD, dataflow and the constraints related to either."""
    DATA_STRUCTURE = "datastructure"
    """DSD and its related constraints."""
    PROVISION_AGREEMENT = "provisionagreement"
    """DSD, dataflow, provision agreement and their related constraints."""


url_templates = {
    "agency": "structure/agencyscheme/{0}",
    "category": (
        "structure/categoryscheme/{0}/{1}/{2}"
        "?detail=referencepartial&references=parentsandsiblings"
    ),
    "code": "structure/codelist/{0}/{1}/{2}",
    "code_map": "structure/representationmap/{0}/{1}/{2}",
    "concept": "structure/conceptscheme/{0}/{1}/{2}?references=codelist",
    "dataflow": (
        "structure/dataflow/{0}/{1}/{2}"
        "?detail=referencepartial&references={3}"
    ),
    "hierarchy": (
        "structure/hierarchy/{0}/{1}/{2}"
        "?detail=referencepartial&references=codelist"
    ),
    "mapping": (
        "structure/structuremap/{0}/{1}/{2}"
        "?detail=referencepartial&references=children"
    ),
    "provider": "structure/dataproviderscheme/{0}?references={1}",
    "report": "metadata/metadataset/{0}/{1}/{2}",
    "reports": "metadata/structure/{0}/{1}/{2}/{3}",
    "schema": "schema/{0}/{1}/{2}/{3}",
    "vl": "structure/valuelist/{0}/{1}/{2}",
}


class __BaseRegistryClient:
    __schema_q = [DataflowDetails.ALL, DataflowDetails.SCHEMA]
    __prov_q = [DataflowDetails.ALL, DataflowDetails.PROVIDERS]

    def __init__(
        self,
        api_endpoint: str,
        fmt: Format = Format.SDMX_JSON,
        pem: Optional[str] = None,
    ):
        """Instantiate a new client against the target endpoint."""
        if not api_endpoint.endswith("/"):
            api_endpoint = f"{api_endpoint}/"
        self.api_endpoint = api_endpoint
        self.format = fmt
        if fmt == Format.FUSION_JSON:
            self.deser = fusion_deserializers
        else:
            self.deser = sdmx_deserializers
        self.ssl_context = (
            httpx.create_ssl_context(
                verify=pem,
            )
            if pem
            else httpx.create_ssl_context()
        )
        self.headers = {
            "Accept": self.format.value,
            "Accept-Encoding": "gzip, deflate",
        }

    def _out(self, response: bytes, typ: Deserializer, *params: Any) -> Any:
        return decode(response, type=typ).to_model(*params)

    def _url(self, typ: str, *params: str) -> str:
        self._check(*params)
        return f"{self.api_endpoint}{url_templates[typ].format(*params)}"

    def _check(self, *params: str) -> None:
        for p in params:
            if not isinstance(p, str):
                msg = (
                    "All parameters must be set and must be strings."
                    "Please check the documentation for the function "
                    "you called and try again."
                )
                raise ClientError(400, "Validation issue", msg)

    def _error(
        self,
        e: Union[httpx.RequestError, httpx.HTTPStatusError],
    ) -> NoReturn:
        q = e.request.url
        if isinstance(e, httpx.HTTPStatusError):
            s = e.response.status_code
            t = e.response.text
            if s == 404:
                msg = (
                    "The requested artefact could not be found in the "
                    f"targeted registry. The query was `{q}`"
                )
                raise NotFound(s, "Not found", msg) from e
            elif s < 500:
                msg = (
                    f"The query returned a {s} error code. The query "
                    f"was `{q}`. The error message was: `{t}`."
                )
                raise ClientError(s, f"Client error {s}", msg) from e
            else:
                msg = (
                    f"The service returned a {s} error code. The query "
                    f"was `{q}`. The error message was: `{t}`."
                )
                raise ServiceError(s, f"Service error {s}", msg) from e
        else:
            msg = (
                f"There was an issue connecting to the targeted registry. "
                f"The query was `{q}`. The error message was: `{e}`."
            )
            raise Unavailable(503, "Connection error", msg) from e

    def _df_details(self, details: DataflowDetails) -> Tuple[bool, str]:
        sq = False
        dr = "none"
        if details in self.__schema_q:
            sq = True
        if details in self.__prov_q:
            dr = "parentsandsiblings"
        return (sq, dr)


class RegistryClient(__BaseRegistryClient):
    """A client to be used to retrieve metadata from the FMR.

    With this client, metadata will be retrieved in a synchronous fashion.
    """

    def __init__(
        self,
        api_endpoint: str,
        format: Format = Format.SDMX_JSON,
        pem: Optional[str] = None,
    ):
        """Instantiate a new client against the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            format: The format the service should use to serialize
                the metadata to be returned. Defaults to SDMX-JSON.
            pem: In case the service exposed a certificate created
                by an unknown certificate authority, you can pass
                a pem file for this authority using this parameter.
        """
        super().__init__(api_endpoint, format, pem)

    def __fetch(self, url: str, is_ref_meta: bool = False) -> bytes:
        with httpx.Client(verify=self.ssl_context) as client:
            try:
                if is_ref_meta and self.format == Format.SDMX_JSON:
                    h = self.headers.copy()
                    h[
                        "Accept"
                    ] = "application/vnd.sdmx.metadata+json;version=2.0.0"
                else:
                    h = self.headers
                r = client.get(url, headers=h)
                r.raise_for_status()
                return r.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._error(e)

    def get_agencies(self, agency: str) -> Sequence[Organisation]:
        """Get the list of **sub-agencies** for the supplied agency.

        Args:
            agency: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        out = self.__fetch(super()._url("agency", agency))
        return super()._out(out, self.deser.agencies)

    def get_providers(
        self,
        agency: str,
        with_flows: bool = False,
    ) -> Sequence[Organisation]:
        """Get the list of **data providers** for the supplied agency.

        Args:
            agency: The agency maintaining the data provider scheme from
                which data providers must be returned.
            with_flows: Whether the data providers should contain the list
                of dataflows for which the data provider provides data.

        Returns:
            The requested list of data providers.
        """
        ref = "provisionagreement" if with_flows else "none"
        out = self.__fetch(super()._url("provider", agency, ref))
        return super()._out(out, self.deser.providers)

    def get_categories(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> CategoryScheme:
        """Get the category scheme matching the supplied parameters.

        Args:
            agency: The agency maintaining the category scheme.
            id: The ID of the category scheme to be returned.
            version: The version of the category scheme to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested category scheme.
        """
        out = self.__fetch(super()._url("category", agency, id, version))
        return super()._out(out, self.deser.categories)

    def get_codes(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> Codelist:
        """Get the codelist or valuelist matching the supplied parameters.

        Args:
            agency: The agency maintaining the codelist.
            id: The ID of the codelist to be returned.
            version: The version of the codelist to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested codelist.
        """
        try:
            out = self.__fetch(super()._url("code", agency, id, version))
            return super()._out(out, self.deser.codes)
        except NotFound:
            out = self.__fetch(super()._url("vl", agency, id, version))
            return super()._out(out, self.deser.codes)

    def get_concepts(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> ConceptScheme:
        """Get the concept scheme matching the supplied parameters.

        Args:
            agency: The agency maintaining the concept scheme.
            id: The ID of the concept scheme to be returned.
            version: The version of the concept scheme to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested concept scheme.
        """
        out = self.__fetch(super()._url("concept", agency, id, version))
        return super()._out(out, self.deser.concepts)

    def get_schema(
        self,
        context: Union[
            Context, Literal["dataflow", "datastructure", "provisionagreement"]
        ],
        agency: str,
        id: str,
        version: str,
    ) -> Schema:
        """Get the schema matching the supplied parameters.

        Args:
            context: The context for which the schema should be generated
                (dataflow, datastructure or provisionagreement). This defines
                the constraints to be applied when generating the schema.
            agency: The ID of the agency maintaining the context.
            id: The ID of the context to be considered.
            version: The version of the context to be considered.

        Returns:
            The requested schema.
        """
        c = context.value if isinstance(context, Context) else context
        out = self.__fetch(super()._url("schema", c, agency, id, version))
        return super()._out(
            out,
            self.deser.schema,
            c,
            agency,
            id,
            version,
        )

    def get_dataflow_details(
        self,
        agency: str,
        id: str,
        version: str = "+",
        detail: Union[
            DataflowDetails, Literal["all", "core", "providers", "schema"]
        ] = DataflowDetails.ALL,
    ) -> DataflowInfo:
        """Get detailed information about a dataflow.

        Args:
            agency: The agency maintaining the dataflow.
            id: The ID of the dataflow to be returned.
            version: The version of the dataflow to be returned. The most
                recent version will be returned, unless specified otherwise.
            detail: The amount of detail to be returned. "core" means only
                core information (ID, name, etc.) will be returned.
                "providers" means core information will be returned, as well
                as the list of organizations providing data for the dataflow.
                "schema" means core information will be returned, as well
                as the schema describing the expected/allowed structure of
                data to be reported against the dataflow. "all" combines all
                3 other options.

        Returns:
            The requested information about a dataflow.
        """
        d = DataflowDetails(detail) if isinstance(detail, str) else detail
        sq, dr = super()._df_details(d)
        if sq:
            cmps = self.get_schema("dataflow", agency, id, version).components
        else:
            cmps = None
        out = self.__fetch(super()._url("dataflow", agency, id, version, dr))
        return super()._out(
            out, self.deser.dataflow, cmps, agency, id, version
        )

    def get_hierarchy(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> Hierarchy:
        """Get a hierarchical list of codes.

        Args:
            agency: The agency maintaining the hierarchy.
            id: The ID of the hierarchy to be returned.
            version: The version of the hierarchy to be returned. The most
                recent version will be returned, unless specified otherwise.

        Returns:
            The requested hierarchical list of codes.
        """
        out = self.__fetch(super()._url("hierarchy", agency, id, version))
        return super()._out(out, self.deser.hierarchy)

    def get_report(
        self,
        provider: str,
        id: str,
        version: str = "+",
    ) -> MetadataReport:
        """Get a reference metadata report.

        Args:
            provider: The organization which provided the report.
            id: The ID of the report to be returned.
            version: The version of the report to be returned. The most
                recent version will be returned, unless specified otherwise.

        Returns:
            The requested metadata report.
        """
        out = self.__fetch(super()._url("report", provider, id, version), True)
        return super()._out(out, self.deser.report)

    def get_reports(
        self,
        artefact_type: str,
        agency: str,
        id: str,
        version: str = "+",
    ) -> Sequence[MetadataReport]:
        """Get the reference metadata reports for the supplied structure.

        Args:
            artefact_type: The type of the structure for which reports must
                be returned.
            agency: The agency maintaining the hierarchy for which reports
                must be returned.
            id: The ID of the structure for which reports must be returned.
            version: The version of the structure for which reports must be
                returned.

        Returns:
            The metadata reports about the supplied structure.
        """
        out = self.__fetch(
            super()._url("reports", artefact_type, agency, id, version), True
        )
        return super()._out(out, self.deser.report, True)

    def get_mapping(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> StructureMap:
        """Get a mapping definition (aka structure map).

        Args:
            agency: The agency maintaining the structure map.
            id: The ID of the structure map to be returned.
            version: The version of the structure map to be returned. The most
                recent version will be returned, unless specified otherwise.

        Returns:
            The requested mapping definition (aka Structure Map).
        """
        out = self.__fetch(super()._url("mapping", agency, id, version))
        return super()._out(out, self.deser.mapping)

    def get_code_map(
        self, agency: str, id: str, version: str = "+"
    ) -> Sequence[ValueMap]:
        """Get a code map (aka representation map).

        Args:
            agency: The agency maintaining the representation map.
            id: The ID of the representation map to be returned.
            version: The version of the representation map to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested mappings in the representation map.
        """
        out = self.__fetch(super()._url("code_map", agency, id, version))
        return super()._out(out, self.deser.code_map)


class AsyncRegistryClient(__BaseRegistryClient):
    """A client to be used to retrieve metadata from the FMR.

    With this client, metadata will be retrieved in a asynchronous fashion.
    """

    def __init__(
        self,
        api_endpoint: str,
        format: Format = Format.SDMX_JSON,
        pem: Optional[str] = None,
    ):
        """Instantiate a new client against the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            format: The format the service should use to serialize
                the metadata to be returned. Defaults to SDMX-JSON.
            pem: In case the service exposed a certificate created
                by an unknown certificate authority, you can pass
                a pem file for this authority using this parameter.
        """
        super().__init__(api_endpoint, format, pem)

    async def __fetch(self, url: str, is_ref_meta: bool = False) -> bytes:
        async with httpx.AsyncClient(
            verify=self.ssl_context,
            timeout=10.0,
        ) as client:
            try:
                if is_ref_meta and self.format == Format.SDMX_JSON:
                    h = self.headers.copy()
                    h[
                        "Accept"
                    ] = "application/vnd.sdmx.metadata+json;version=2.0.0"
                else:
                    h = self.headers
                r = await client.get(url, headers=h)
                r.raise_for_status()
                return r.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._error(e)

    async def get_agencies(self, agency: str) -> Sequence[Organisation]:
        """Get the list of **sub-agencies** for the supplied agency.

        Args:
            agency: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        out = await self.__fetch(super()._url("agency", agency))
        return super()._out(out, self.deser.agencies)

    async def get_providers(
        self, agency: str, with_flows: bool = False
    ) -> Sequence[Organisation]:
        """Get the list of **data providers** for the supplied agency.

        Args:
            agency: The agency maintaining the data provider scheme from
                which data providers must be returned.
            with_flows: Whether the data providers should contain the list
                of dataflows for which the data provider provides data.

        Returns:
            The requested list of data providers.
        """
        ref = "provisionagreement" if with_flows else "none"
        out = await self.__fetch(super()._url("provider", agency, ref))
        return super()._out(out, self.deser.providers)

    async def get_categories(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> CategoryScheme:
        """Get the category scheme matching the supplied parameters.

        Args:
            agency: The agency maintaining the category scheme.
            id: The ID of the category scheme to be returned.
            version: The version of the category scheme to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested category scheme.
        """
        out = await self.__fetch(super()._url("category", agency, id, version))
        return super()._out(out, self.deser.categories)

    async def get_codes(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> Codelist:
        """Get the codes from the codelist matching the supplied parameters.

        Args:
            agency: The agency maintaining the codelist.
            id: The ID of the codelist to be returned.
            version: The version of the codelist to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested codelist.
        """
        try:
            out = await self.__fetch(super()._url("code", agency, id, version))
            return super()._out(out, self.deser.codes)
        except NotFound:
            out = await self.__fetch(super()._url("vl", agency, id, version))
            return super()._out(out, self.deser.codes)

    async def get_concepts(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> ConceptScheme:
        """Get the concept scheme matching the supplied parameters.

        Args:
            agency: The agency maintaining the concept scheme.
            id: The ID of the concept scheme to be returned.
            version: The version of the concept scheme to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested concept scheme.
        """
        out = await self.__fetch(super()._url("concept", agency, id, version))
        return super()._out(out, self.deser.concepts)

    async def get_schema(
        self,
        context: Union[
            Context, Literal["dataflow", "datastructure", "provisionagreement"]
        ],
        agency: str,
        id: str,
        version: str,
    ) -> Schema:
        """Get the schema matching the supplied parameters.

        Args:
            context: The context for which the schema should be generated
                (dataflow, datastructure or provisionagreement). This defines
                the constraints to be applied when generating the schema.
            agency: The ID of the agency maintaining the context.
            id: The ID of the context to be considered.
            version: The version of the context to be considered.

        Returns:
            The requested schema.
        """
        c = context.value if isinstance(context, Context) else context
        r = await self.__fetch(super()._url("schema", c, agency, id, version))
        return super()._out(
            r,
            self.deser.schema,
            c,
            agency,
            id,
            version,
        )

    async def get_dataflow_details(
        self,
        agency: str,
        id: str,
        version: str = "+",
        detail: Union[
            DataflowDetails, Literal["all", "core", "providers", "schema"]
        ] = DataflowDetails.ALL,
    ) -> DataflowInfo:
        """Get detailed information about a dataflow.

        Args:
            agency: The agency maintaining the dataflow.
            id: The ID of the dataflow to be returned.
            version: The version of the dataflow to be returned. The most
                recent version will be returned, unless specified otherwise.
            detail: The amount of detail to be returned. "core" means only
                core information (ID, name, etc.) will be returned.
                "providers" means core information will be returned, as well
                as the list of organizations providing data for the dataflow.
                "schema" means core information will be returned, as well
                as the schema describing the expected/allowed structure of
                data to be reported against the dataflow. "all" combines all
                3 other options.

        Returns:
            The requested information about a dataflow.
        """
        d = DataflowDetails(detail) if isinstance(detail, str) else detail
        sq, dr = super()._df_details(d)
        if sq:
            schema = await self.get_schema(
                "dataflow",
                agency,
                id,
                version,
            )
            cmps = schema.components
        else:
            cmps = None
        out = await self.__fetch(
            super()._url("dataflow", agency, id, version, dr)
        )
        return super()._out(
            out, self.deser.dataflow, cmps, agency, id, version
        )

    async def get_hierarchy(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> Hierarchy:
        """Get a hierarchical list of codes.

        Args:
            agency: The agency maintaining the hierarchy.
            id: The ID of the hierarchy to be returned.
            version: The version of the hierarchy to be returned. The most
                recent version will be returned, unless specified otherwise.

        Returns:
            The requested hierarchical list of codes.
        """
        out = await self.__fetch(
            super()._url(
                "hierarchy",
                agency,
                id,
                version,
            )
        )
        return super()._out(out, self.deser.hierarchy)

    async def get_report(
        self,
        provider: str,
        id: str,
        version: str = "+",
    ) -> MetadataReport:
        """Get a reference metadata report.

        Args:
            provider: The organization which provided the report.
            id: The ID of the report to be returned.
            version: The version of the report to be returned. The most
                recent version will be returned, unless specified otherwise.

        Returns:
            The requested metadata report.
        """
        out = await self.__fetch(
            super()._url("report", provider, id, version), True
        )
        return super()._out(out, self.deser.report)

    async def get_reports(
        self,
        artefact_type: str,
        agency: str,
        id: str,
        version: str = "+",
    ) -> Sequence[MetadataReport]:
        """Get the reference metadata reports for the supplied structure.

        Args:
            artefact_type: The type of the structure for which reports must
                be returned.
            agency: The agency maintaining the hierarchy for which reports
                must be returned.
            id: The ID of the structure for which reports must be returned.
            version: The version of the structure for which reports must be
                returned.

        Returns:
            The metadata reports about the supplied structure.
        """
        out = await self.__fetch(
            super()._url("reports", artefact_type, agency, id, version), True
        )
        return super()._out(out, self.deser.report, True)

    async def get_mapping(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> StructureMap:
        """Get a mapping definition (aka structure map).

        Args:
            agency: The agency maintaining the structure map.
            id: The ID of the structure map to be returned.
            version: The version of the structure map to be returned. The most
                recent version will be returned, unless specified otherwise.

        Returns:
            The requested mapping definition (aka Structure Map).
        """
        out = await self.__fetch(super()._url("mapping", agency, id, version))
        return super()._out(out, self.deser.mapping)

    async def get_code_map(
        self, agency: str, id: str, version: str = "+"
    ) -> Sequence[ValueMap]:
        """Get a code map (aka representation map).

        Args:
            agency: The agency maintaining the representation map.
            id: The ID of the representation map to be returned.
            version: The version of the representation map to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested mappings in the representation map.
        """
        out = await self.__fetch(super()._url("code_map", agency, id, version))
        return super()._out(out, self.deser.code_map)
