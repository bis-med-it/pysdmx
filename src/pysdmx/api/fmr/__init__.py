"""Retrieve metadata from an FMR instance."""

from enum import Enum
from typing import (
    Any,
    Literal,
    NoReturn,
    Optional,
    Sequence,
    Tuple,
    Union,
)

import httpx
from msgspec.json import decode

from pysdmx.api.fmr.reader import Deserializer
from pysdmx.api.qb import (
    ApiVersion,
    RefMetaByMetadatasetQuery,
    RefMetaByStructureQuery,
    SchemaContext,
    SchemaQuery,
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.errors import InternalError, Invalid, NotFound, Unavailable
from pysdmx.io.json.fusion.reader import deserializers as fusion_readers
from pysdmx.io.json.sdmxjson2.reader import deserializers as sdmx_readers
from pysdmx.model import (
    Agency,
    CategoryScheme,
    Codelist,
    ConceptScheme,
    DataflowInfo,
    DataProvider,
    Hierarchy,
    HierarchyAssociation,
    MetadataReport,
    MultiRepresentationMap,
    RepresentationMap,
    Schema,
    StructureMap,
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


API_VERSION = ApiVersion.V2_0_0


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
        if api_endpoint.endswith("/"):
            api_endpoint = api_endpoint[0:-1]
        self.api_endpoint = api_endpoint
        self.format = fmt
        if fmt == Format.FUSION_JSON:
            self.deser = fusion_readers
        else:
            self.deser = sdmx_readers
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
                raise NotFound("Not found", msg) from e
            elif s < 500:
                msg = (
                    f"The query returned a {s} error code. The query "
                    f"was `{q}`. The error message was: `{t}`."
                )
                raise Invalid(f"Client error {s}", msg) from e
            else:
                msg = (
                    f"The service returned a {s} error code. The query "
                    f"was `{q}`. The error message was: `{t}`."
                )
                raise InternalError(f"Service error {s}", msg) from e
        else:
            msg = (
                f"There was an issue connecting to the targeted registry. "
                f"The query was `{q}`. The error message was: `{e}`."
            )
            raise Unavailable("Connection error", msg) from e

    def _df_details(
        self, details: DataflowDetails
    ) -> Tuple[bool, StructureReference]:
        sq = False
        dr = StructureReference.NONE
        if details in self.__schema_q:
            sq = True
        if details in self.__prov_q:
            dr = StructureReference.PARENTSANDSIBLINGS
        return (sq, dr)

    def _hierarchies_for_flow_url(
        self, agency: str, flow: str, version: str
    ) -> str:
        d = StructureDetail.REFERENCE_PARTIAL
        r = StructureReference.ALL
        q = StructureQuery(
            StructureType.DATAFLOW,
            agency,
            flow,
            version,
            detail=d,
            references=r,
        )
        return q.get_url(API_VERSION, True)

    def _hierarchies_for_pra_url(
        self, agency: str, pra: str, version: str
    ) -> str:
        d = StructureDetail.REFERENCE_PARTIAL
        r = StructureReference.ALL
        q = StructureQuery(
            StructureType.PROVISION_AGREEMENT,
            agency,
            pra,
            version,
            detail=d,
            references=r,
        )
        return q.get_url(API_VERSION, True)

    def _code_map_url(self, agency: str, id: str, version: str) -> str:
        q = StructureQuery(
            StructureType.REPRESENTATION_MAP, agency, id, version
        )
        return q.get_url(API_VERSION, True)

    def _mapping_url(self, agency: str, id: str, version: str) -> str:
        r = StructureReference.CHILDREN
        d = StructureDetail.REFERENCE_PARTIAL
        q = StructureQuery(
            StructureType.STRUCTURE_MAP,
            agency,
            id,
            version,
            detail=d,
            references=r,
        )
        return q.get_url(API_VERSION, True)

    def _reports_url(
        self, artefact_type: str, agency: str, id: str, version: str
    ) -> str:
        q = RefMetaByStructureQuery(
            StructureType(artefact_type), agency, id, version
        )
        return q.get_url(API_VERSION, True)

    def _report_url(self, provider: str, id: str, version: str) -> str:
        q = RefMetaByMetadatasetQuery(provider, id, version)
        return q.get_url(API_VERSION, True)

    def _hierarchy_url(self, agency: str, id: str, version: str) -> str:
        q = StructureQuery(
            StructureType.HIERARCHY,
            agency,
            id,
            version,
            detail=StructureDetail.REFERENCE_PARTIAL,
            references=StructureReference.CODELIST,
        )
        return q.get_url(API_VERSION, True)

    def _agencies_url(self, agency: str) -> str:
        q = StructureQuery(StructureType.AGENCY_SCHEME, agency)
        return q.get_url(API_VERSION, True)

    def _providers_url(self, agency: str, with_flows: bool) -> str:
        r = (
            StructureReference.PROVISION_AGREEMENT
            if with_flows
            else StructureReference.NONE
        )
        q = StructureQuery(
            StructureType.DATA_PROVIDER_SCHEME, agency, references=r
        )
        return q.get_url(API_VERSION, True)

    def _categories_url(self, agency: str, id: str, version: str) -> str:
        q = StructureQuery(
            StructureType.CATEGORY_SCHEME,
            agency,
            id,
            version,
            detail=StructureDetail.REFERENCE_PARTIAL,
            references=StructureReference.PARENTSANDSIBLINGS,
        )
        return q.get_url(API_VERSION, True)

    def _codes_cl_url(self, agency: str, id: str, version: str) -> str:
        q = StructureQuery(StructureType.CODELIST, agency, id, version)
        return q.get_url(API_VERSION, True)

    def _codes_vl_url(self, agency: str, id: str, version: str) -> str:
        q = StructureQuery(StructureType.VALUE_LIST, agency, id, version)
        return q.get_url(API_VERSION, True)

    def _concepts_url(self, agency: str, id: str, version: str) -> str:
        q = StructureQuery(
            StructureType.CONCEPT_SCHEME,
            agency,
            id,
            version,
            references=StructureReference.CODELIST,
        )
        return q.get_url(API_VERSION, True)

    def _schema_url(
        self, context: SchemaContext, agency: str, id: str, version: str
    ) -> str:
        q = SchemaQuery(context, agency, id, version)
        return q.get_url(API_VERSION, True)

    def _dataflow_details_url(
        self, agency: str, id: str, version: str, ref: StructureReference
    ) -> str:
        q = StructureQuery(
            StructureType.DATAFLOW,
            agency,
            id,
            version,
            detail=StructureDetail.REFERENCE_PARTIAL,
            references=ref,
        )
        return q.get_url(API_VERSION, True)


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
                    h["Accept"] = (
                        "application/vnd.sdmx.metadata+json;version=2.0.0"
                    )
                else:
                    h = self.headers
                r = client.get(url, headers=h)
                r.raise_for_status()
                return r.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._error(e)

    def __get_hierarchies_for_flow(
        self, agency: str, flow: str, version: str
    ) -> Sequence[HierarchyAssociation]:
        url = super()._hierarchies_for_flow_url(agency, flow, version)
        out = self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(out, self.deser.hier_assoc)

    def __get_hierarchies_for_pra(
        self, agency: str, pra: str, version: str
    ) -> Sequence[HierarchyAssociation]:
        url = super()._hierarchies_for_pra_url(agency, pra, version)
        out = self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(out, self.deser.hier_assoc)

    def get_agencies(self, agency: str) -> Sequence[Agency]:
        """Get the list of **sub-agencies** for the supplied agency.

        Args:
            agency: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        url = super()._agencies_url(agency)
        out = self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(out, self.deser.agencies)

    def get_providers(
        self,
        agency: str,
        with_flows: bool = False,
    ) -> Sequence[DataProvider]:
        """Get the list of **data providers** for the supplied agency.

        Args:
            agency: The agency maintaining the data provider scheme from
                which data providers must be returned.
            with_flows: Whether the data providers should contain the list
                of dataflows for which the data provider provides data.

        Returns:
            The requested list of data providers.
        """
        url = super()._providers_url(agency, with_flows)
        out = self.__fetch(f"{self.api_endpoint}{url}")
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
        url = super()._categories_url(agency, id, version)
        out = self.__fetch(f"{self.api_endpoint}{url}")
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
            url = super()._codes_cl_url(agency, id, version)
            out = self.__fetch(f"{self.api_endpoint}{url}")
            return super()._out(out, self.deser.codes)
        except NotFound:
            url = super()._codes_vl_url(agency, id, version)
            out = self.__fetch(f"{self.api_endpoint}{url}")
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
        url = super()._concepts_url(agency, id, version)
        out = self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(out, self.deser.concepts)

    def get_schema(
        self,
        context: Union[
            SchemaContext,
            Literal["dataflow", "datastructure", "provisionagreement"],
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
        c = (
            context
            if isinstance(context, SchemaContext)
            else SchemaContext(context)
        )
        if c == SchemaContext.DATAFLOW:
            ha = self.__get_hierarchies_for_flow(agency, id, version)
        elif c == SchemaContext.PROVISION_AGREEMENT:
            ha = self.__get_hierarchies_for_pra(agency, id, version)
        else:
            ha = ()
        url = super()._schema_url(c, agency, id, version)
        out = self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(
            out, self.deser.schema, c.value, agency, id, version, ha
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
        url = super()._dataflow_details_url(agency, id, version, dr)
        out = self.__fetch(f"{self.api_endpoint}{url}")
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
        url = super()._hierarchy_url(agency, id, version)
        out = self.__fetch(f"{self.api_endpoint}{url}")
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
        url = super()._report_url(provider, id, version)
        out = self.__fetch(f"{self.api_endpoint}{url}", True)
        return super()._out(out, self.deser.report)[0]

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
        url = super()._reports_url(artefact_type, agency, id, version)
        out = self.__fetch(f"{self.api_endpoint}{url}", True)
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
        url = super()._mapping_url(agency, id, version)
        out = self.__fetch(f"{self.api_endpoint}{url}", True)
        return super()._out(out, self.deser.mapping)

    def get_code_map(
        self, agency: str, id: str, version: str = "+"
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
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
        url = super()._code_map_url(agency, id, version)
        out = self.__fetch(f"{self.api_endpoint}{url}", True)
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
                    h["Accept"] = (
                        "application/vnd.sdmx.metadata+json;version=2.0.0"
                    )
                else:
                    h = self.headers
                r = await client.get(url, headers=h)
                r.raise_for_status()
                return r.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._error(e)

    async def __get_hierarchies_for_flow(
        self, agency: str, flow: str, version: str
    ) -> Sequence[HierarchyAssociation]:
        url = super()._hierarchies_for_flow_url(agency, flow, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(out, self.deser.hier_assoc)

    async def __get_hierarchies_for_pra(
        self, agency: str, pra: str, version: str
    ) -> Sequence[HierarchyAssociation]:
        url = super()._hierarchies_for_pra_url(agency, pra, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(out, self.deser.hier_assoc)

    async def get_agencies(self, agency: str) -> Sequence[Agency]:
        """Get the list of **sub-agencies** for the supplied agency.

        Args:
            agency: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        url = super()._agencies_url(agency)
        out = await self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(out, self.deser.agencies)

    async def get_providers(
        self, agency: str, with_flows: bool = False
    ) -> Sequence[DataProvider]:
        """Get the list of **data providers** for the supplied agency.

        Args:
            agency: The agency maintaining the data provider scheme from
                which data providers must be returned.
            with_flows: Whether the data providers should contain the list
                of dataflows for which the data provider provides data.

        Returns:
            The requested list of data providers.
        """
        url = super()._providers_url(agency, with_flows)
        out = await self.__fetch(f"{self.api_endpoint}{url}")
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
        url = super()._categories_url(agency, id, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}")
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
            url = super()._codes_cl_url(agency, id, version)
            out = await self.__fetch(f"{self.api_endpoint}{url}")
            return super()._out(out, self.deser.codes)
        except NotFound:
            url = super()._codes_vl_url(agency, id, version)
            out = await self.__fetch(f"{self.api_endpoint}{url}")
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
        url = super()._concepts_url(agency, id, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(out, self.deser.concepts)

    async def get_schema(
        self,
        context: Union[
            SchemaContext,
            Literal["dataflow", "datastructure", "provisionagreement"],
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
        c = (
            context
            if isinstance(context, SchemaContext)
            else SchemaContext(context)
        )
        if c == SchemaContext.DATAFLOW:
            ha = await self.__get_hierarchies_for_flow(agency, id, version)
        elif c == SchemaContext.PROVISION_AGREEMENT:
            ha = await self.__get_hierarchies_for_pra(agency, id, version)
        else:
            ha = ()
        url = super()._schema_url(c, agency, id, version)
        r = await self.__fetch(f"{self.api_endpoint}{url}")
        return super()._out(
            r, self.deser.schema, c.value, agency, id, version, ha
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
        url = super()._dataflow_details_url(agency, id, version, dr)
        out = await self.__fetch(f"{self.api_endpoint}{url}")
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
        url = super()._hierarchy_url(agency, id, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}")
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
        url = super()._report_url(provider, id, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}", True)
        return super()._out(out, self.deser.report)[0]

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
        url = super()._reports_url(artefact_type, agency, id, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}", True)
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
        url = super()._mapping_url(agency, id, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}", True)
        return super()._out(out, self.deser.mapping)

    async def get_code_map(
        self, agency: str, id: str, version: str = "+"
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
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
        url = super()._code_map_url(agency, id, version)
        out = await self.__fetch(f"{self.api_endpoint}{url}", True)
        return super()._out(out, self.deser.code_map)
