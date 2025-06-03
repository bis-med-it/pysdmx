"""Retrieve metadata from an FMR instance."""

from enum import Enum
from typing import (
    Any,
    Literal,
    Optional,
    Sequence,
    Tuple,
    Union,
)

from msgspec.json import decode

from pysdmx.api.qb import (
    ApiVersion,
    AsyncRestService,
    RefMetaByMetadatasetQuery,
    RefMetaByStructureQuery,
    RestService,
    SchemaContext,
    SchemaQuery,
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.errors import NotFound, NotImplemented
from pysdmx.io.format import RefMetaFormat, SchemaFormat, StructureFormat
from pysdmx.io.json.fusion.reader import deserializers as fusion_readers
from pysdmx.io.json.sdmxjson2.reader import deserializers as sdmx_readers
from pysdmx.io.serde import Deserializer
from pysdmx.model import (
    Agency,
    Categorisation,
    CategoryScheme,
    Codelist,
    ConceptScheme,
    Dataflow,
    DataflowInfo,
    DataProvider,
    Hierarchy,
    HierarchyAssociation,
    MetadataReport,
    MultiRepresentationMap,
    ProvisionAgreement,
    RepresentationMap,
    Schema,
    StructureMap,
)


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
        fmt: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
    ):
        """Instantiate a new client against the target endpoint."""
        if api_endpoint.endswith("/"):
            api_endpoint = api_endpoint[0:-1]
        self.api_endpoint = api_endpoint
        if fmt not in (
            StructureFormat.SDMX_JSON_2_0_0,
            StructureFormat.FUSION_JSON,
        ):
            raise NotImplemented(
                "Unsupported format",
                "Only SDMX-JSON v2.0.0 and Fusion-JSON are supported.",
                {"requested_format": fmt.value},
            )
        self.format = fmt
        if fmt == StructureFormat.FUSION_JSON:
            self.deser = fusion_readers
        else:
            self.deser = sdmx_readers

    def _out(self, response: bytes, typ: Deserializer, *params: Any) -> Any:
        return decode(response, type=typ).to_model(*params)

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

    def _hierarchies_for_flow_q(
        self, agency: str, flow: str, version: str
    ) -> StructureQuery:
        d = StructureDetail.REFERENCE_PARTIAL
        r = StructureReference.ALL
        return StructureQuery(
            StructureType.DATAFLOW,
            agency,
            flow,
            version,
            detail=d,
            references=r,
        )

    def _hierarchies_for_pra_q(
        self, agency: str, pra: str, version: str
    ) -> StructureQuery:
        d = StructureDetail.REFERENCE_PARTIAL
        r = StructureReference.ALL
        return StructureQuery(
            StructureType.PROVISION_AGREEMENT,
            agency,
            pra,
            version,
            detail=d,
            references=r,
        )

    def _code_map_q(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        return StructureQuery(
            StructureType.REPRESENTATION_MAP, agency, id, version
        )

    def _mapping_q(self, agency: str, id: str, version: str) -> StructureQuery:
        r = StructureReference.CHILDREN
        d = StructureDetail.REFERENCE_PARTIAL
        return StructureQuery(
            StructureType.STRUCTURE_MAP,
            agency,
            id,
            version,
            detail=d,
            references=r,
        )

    def _reports_q(
        self,
        artefact_type: str,
        agency: str,
        id: str,
        version: str,
    ) -> RefMetaByStructureQuery:
        return RefMetaByStructureQuery(
            StructureType(artefact_type), agency, id, version
        )

    def _report_q(
        self, provider: str, id: str, version: str
    ) -> RefMetaByMetadatasetQuery:
        return RefMetaByMetadatasetQuery(provider, id, version)

    def _hierarchy_q(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        return StructureQuery(
            StructureType.HIERARCHY,
            agency,
            id,
            version,
            detail=StructureDetail.REFERENCE_PARTIAL,
            references=StructureReference.CODELIST,
        )

    def _agencies_q(self, agency: str) -> StructureQuery:
        return StructureQuery(StructureType.AGENCY_SCHEME, agency)

    def _providers_q(self, agency: str, with_flows: bool) -> StructureQuery:
        r = (
            StructureReference.PROVISION_AGREEMENT
            if with_flows
            else StructureReference.NONE
        )
        return StructureQuery(
            StructureType.DATA_PROVIDER_SCHEME, agency, references=r
        )

    def _categories_q(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        return StructureQuery(
            StructureType.CATEGORY_SCHEME,
            agency,
            id,
            version,
            detail=StructureDetail.REFERENCE_PARTIAL,
            references=StructureReference.PARENTSANDSIBLINGS,
        )

    def _codes_cl_q(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        return StructureQuery(StructureType.CODELIST, agency, id, version)

    def _codes_vl_q(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        return StructureQuery(StructureType.VALUE_LIST, agency, id, version)

    def _concepts_q(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        return StructureQuery(
            StructureType.CONCEPT_SCHEME,
            agency,
            id,
            version,
            references=StructureReference.CODELIST,
        )

    def _schema_q(
        self, context: SchemaContext, agency: str, id: str, version: str
    ) -> SchemaQuery:
        return SchemaQuery(context, agency, id, version)

    def _dataflow_details_q(
        self, agency: str, id: str, version: str, ref: StructureReference
    ) -> StructureQuery:
        return StructureQuery(
            StructureType.DATAFLOW,
            agency,
            id,
            version,
            detail=StructureDetail.REFERENCE_PARTIAL,
            references=ref,
        )

    def _dataflows_q(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        return StructureQuery(StructureType.DATAFLOW, agency, id, version)

    def _vtl_ts_q(self, agency: str, id: str, version: str) -> StructureQuery:
        return StructureQuery(
            StructureType.TRANSFORMATION_SCHEME,
            agency,
            id,
            version,
            detail=StructureDetail.REFERENCE_PARTIAL,
            references=StructureReference.DESCENDANTS,
        )

    def _categorisation_q(
        self, agency: str, id: str, version: str
    ) -> StructureQuery:
        return StructureQuery(
            StructureType.CATEGORISATION, agency, id, version
        )

    def _pa_q(self, agency: str, id: str, version: str) -> StructureQuery:
        return StructureQuery(
            StructureType.PROVISION_AGREEMENT, agency, id, version
        )


class RegistryClient(__BaseRegistryClient):
    """A client to be used to retrieve metadata from the FMR.

    With this client, metadata will be retrieved in a synchronous fashion.
    """

    def __init__(
        self,
        api_endpoint: str,
        format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        pem: Optional[str] = None,
        timeout: float = 10.0,
    ):
        """Instantiate a new client against the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            format: The format the service should use to serialize
                the metadata to be returned. Defaults to SDMX-JSON.
            pem: In case the service exposed a certificate created
                by an unknown certificate authority, you can pass
                a pem file for this authority using this parameter.
            timeout: The maximum number of seconds to wait before
                considering that a request timed out. Defaults to
                10 seconds.
        """
        super().__init__(api_endpoint, format)
        self.__service = RestService(
            self.api_endpoint,
            API_VERSION,
            structure_format=format,
            schema_format=(
                SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE
                if format == StructureFormat.SDMX_JSON_2_0_0
                else SchemaFormat.FUSION_JSON
            ),
            refmeta_format=(
                RefMetaFormat.SDMX_JSON_2_0_0
                if format == StructureFormat.SDMX_JSON_2_0_0
                else RefMetaFormat.FUSION_JSON
            ),
            pem=pem,
            timeout=timeout,
        )

    def __fetch(
        self,
        query: Union[
            RefMetaByMetadatasetQuery,
            RefMetaByStructureQuery,
            SchemaQuery,
            StructureQuery,
        ],
    ) -> bytes:
        if isinstance(query, StructureQuery):
            return self.__service.structure(query)
        elif isinstance(query, SchemaQuery):
            return self.__service.schema(query)
        else:
            return self.__service.reference_metadata(query)

    def __get_hierarchies_for_flow(
        self, agency: str, flow: str, version: str
    ) -> Sequence[HierarchyAssociation]:
        query = super()._hierarchies_for_flow_q(agency, flow, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.hier_assoc)

    def __get_hierarchies_for_pra(
        self, agency: str, pra: str, version: str
    ) -> Sequence[HierarchyAssociation]:
        query = super()._hierarchies_for_pra_q(agency, pra, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.hier_assoc)

    def get_agencies(self, agency: str) -> Sequence[Agency]:
        """Get the list of **sub-agencies** for the supplied agency.

        Args:
            agency: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        query = super()._agencies_q(agency)
        out = self.__fetch(query)
        schemes = super()._out(out, self.deser.agencies)
        return schemes[0].items

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
        query = super()._providers_q(agency, with_flows)
        out = self.__fetch(query)
        schemes = super()._out(out, self.deser.providers)
        return schemes[0].items

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
        query = super()._categories_q(agency, id, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.categories)

    def get_categorisation(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> Categorisation:
        """Get the categorisation matching the supplied parameters.

        Args:
            agency: The agency maintaining the categorisation.
            id: The ID of the categorisation to be returned.
            version: The version of the categorisation to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested categorisation.
        """
        query = super()._categorisation_q(agency, id, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.categorisation)[0]

    def get_provision_agreement(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> ProvisionAgreement:
        """Get the provision agreement matching the supplied parameters.

        Args:
            agency: The agency maintaining the provision agreement.
            id: The ID of the provision agreement to be returned.
            version: The version of the provision agreement to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested provision agreement.
        """
        query = super()._pa_q(agency, id, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.provision_agreement)[0]

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
            query = super()._codes_cl_q(agency, id, version)
            out = self.__fetch(query)
            return super()._out(out, self.deser.codes)
        except NotFound:
            query = super()._codes_vl_q(agency, id, version)
            out = self.__fetch(query)
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
        query = super()._concepts_q(agency, id, version)
        out = self.__fetch(query)
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
        query = super()._schema_q(c, agency, id, version)
        out = self.__fetch(query)
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
        query = super()._dataflow_details_q(agency, id, version, dr)
        out = self.__fetch(query)
        return super()._out(
            out, self.deser.dataflow_info, cmps, agency, id, version
        )

    def get_dataflows(
        self,
        agency: str = "*",
        id: str = "*",
        version: str = "+",
    ) -> Sequence[Dataflow]:
        """Get the dataflow(s) matching the supplied parameters.

        Args:
            agency: The agency maintaining the dataflow(s).
            id: The ID of the dataflow(s) to be returned.
            version: The version of the dataflow(s) to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested dataflow(s).
        """
        query = super()._dataflows_q(agency, id, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.dataflows)

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
        query = super()._hierarchy_q(agency, id, version)
        out = self.__fetch(query)
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
        query = super()._report_q(provider, id, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.report).reports[0]

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
        query = super()._reports_q(artefact_type, agency, id, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.report).reports

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
        query = super()._mapping_q(agency, id, version)
        out = self.__fetch(query)
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
        query = super()._code_map_q(agency, id, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.code_map)

    def get_vtl_transformation_scheme(
        self, agency: str, id: str, version: str = "+"
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Get a VTL transformation scheme.

        Args:
            agency: The agency maintaining the transformation scheme.
            id: The ID of the transformation scheme map to be returned.
            version: The version of the transformation scheme to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested transformation scheme.
        """
        query = super()._vtl_ts_q(agency, id, version)
        out = self.__fetch(query)
        return super()._out(out, self.deser.transformation_scheme)


class AsyncRegistryClient(__BaseRegistryClient):
    """A client to be used to retrieve metadata from the FMR.

    With this client, metadata will be retrieved in a asynchronous fashion.
    """

    def __init__(
        self,
        api_endpoint: str,
        format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        pem: Optional[str] = None,
        timeout: float = 10.0,
    ):
        """Instantiate a new client against the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            format: The format the service should use to serialize
                the metadata to be returned. Defaults to SDMX-JSON.
            pem: In case the service exposed a certificate created
                by an unknown certificate authority, you can pass
                a pem file for this authority using this parameter.
            timeout: The maximum number of seconds to wait before
                considering that a request timed out. Defaults to
                10 seconds.
        """
        super().__init__(api_endpoint, format)
        self.__service = AsyncRestService(
            self.api_endpoint,
            API_VERSION,
            structure_format=format,
            schema_format=(
                SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE
                if format == StructureFormat.SDMX_JSON_2_0_0
                else SchemaFormat.FUSION_JSON
            ),
            refmeta_format=(
                RefMetaFormat.SDMX_JSON_2_0_0
                if format == StructureFormat.SDMX_JSON_2_0_0
                else RefMetaFormat.FUSION_JSON
            ),
            pem=pem,
            timeout=timeout,
        )

    async def __fetch(
        self,
        query: Union[
            RefMetaByMetadatasetQuery,
            RefMetaByStructureQuery,
            SchemaQuery,
            StructureQuery,
        ],
    ) -> bytes:
        if isinstance(query, StructureQuery):
            out = await self.__service.structure(query)
            return out
        elif isinstance(query, SchemaQuery):
            out = await self.__service.schema(query)
            return out
        else:
            out = await self.__service.reference_metadata(query)
            return out

    async def __get_hierarchies_for_flow(
        self, agency: str, flow: str, version: str
    ) -> Sequence[HierarchyAssociation]:
        query = super()._hierarchies_for_flow_q(agency, flow, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.hier_assoc)

    async def __get_hierarchies_for_pra(
        self, agency: str, pra: str, version: str
    ) -> Sequence[HierarchyAssociation]:
        query = super()._hierarchies_for_pra_q(agency, pra, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.hier_assoc)

    async def get_agencies(self, agency: str) -> Sequence[Agency]:
        """Get the list of **sub-agencies** for the supplied agency.

        Args:
            agency: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        query = super()._agencies_q(agency)
        out = await self.__fetch(query)
        schemes = super()._out(out, self.deser.agencies)
        return schemes[0].items

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
        query = super()._providers_q(agency, with_flows)
        out = await self.__fetch(query)
        schemes = super()._out(out, self.deser.providers)
        return schemes[0].items

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
        query = super()._categories_q(agency, id, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.categories)

    async def get_categorisation(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> Categorisation:
        """Get the categorisation matching the supplied parameters.

        Args:
            agency: The agency maintaining the categorisation.
            id: The ID of the categorisation to be returned.
            version: The version of the categorisation to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested categorisation.
        """
        query = super()._categorisation_q(agency, id, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.categorisation)[0]

    async def get_provision_agreement(
        self,
        agency: str,
        id: str,
        version: str = "+",
    ) -> ProvisionAgreement:
        """Get the provision agreement matching the supplied parameters.

        Args:
            agency: The agency maintaining the provision agreement.
            id: The ID of the provision agreement to be returned.
            version: The version of the provision agreement to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested provision agreement.
        """
        query = super()._pa_q(agency, id, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.provision_agreement)[0]

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
            query = super()._codes_cl_q(agency, id, version)
            out = await self.__fetch(query)
            return super()._out(out, self.deser.codes)
        except NotFound:
            query = super()._codes_vl_q(agency, id, version)
            out = await self.__fetch(query)
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
        query = super()._concepts_q(agency, id, version)
        out = await self.__fetch(query)
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
        query = super()._schema_q(c, agency, id, version)
        r = await self.__fetch(query)
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
        query = super()._dataflow_details_q(agency, id, version, dr)
        out = await self.__fetch(query)
        return super()._out(
            out, self.deser.dataflow_info, cmps, agency, id, version
        )

    async def get_dataflows(
        self,
        agency: str = "*",
        id: str = "*",
        version: str = "+",
    ) -> Sequence[Dataflow]:
        """Get the dataflow(s) matching the supplied parameters.

        Args:
            agency: The agency maintaining the dataflow(s).
            id: The ID of the dataflow(s) to be returned.
            version: The version of the dataflow(s) to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested dataflow(s).
        """
        query = super()._dataflows_q(agency, id, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.dataflows)

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
        query = super()._hierarchy_q(agency, id, version)
        out = await self.__fetch(query)
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
        query = super()._report_q(provider, id, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.report).reports[0]

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
        query = super()._reports_q(artefact_type, agency, id, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.report).reports

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
        query = super()._mapping_q(agency, id, version)
        out = await self.__fetch(query)
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
        query = super()._code_map_q(agency, id, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.code_map)

    async def get_vtl_transformation_scheme(
        self, agency: str, id: str, version: str = "+"
    ) -> Union[MultiRepresentationMap, RepresentationMap]:
        """Get a VTL transformation scheme.

        Args:
            agency: The agency maintaining the transformation scheme.
            id: The ID of the transformation scheme map to be returned.
            version: The version of the transformation scheme to be returned.
                The most recent version will be returned, unless specified
                otherwise.

        Returns:
            The requested transformation scheme.
        """
        query = super()._vtl_ts_q(agency, id, version)
        out = await self.__fetch(query)
        return super()._out(out, self.deser.transformation_scheme)
