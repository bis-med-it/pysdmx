from enum import Enum
from typing import FrozenSet

from msgspec import Struct

from pysdmx.errors import ClientError
from pysdmx.api.qb.util import ApiVersion, check_multiple_items


class StructureDetail(Enum):
    FULL = "full"
    ALL_STUBS = "allstubs"
    REFERENCE_STUBS = "referencestubs"
    ALL_COMPLETE_STUBS = "allcompletestubs"
    REFERENCE_COMPLETE_STUBS = "referencecompletestubs"
    REFERENCE_PARTIAL = "referencepartial"
    RAW = "raw"


class StructureReference(Enum):

    NONE = "none"
    PARENTS = "parents"
    PARENTSANDSIBLINGS = "parentsandsiblings"
    ANCESTORS = "ancestors"
    CHILDREN = "children"
    DESCENDANTS = "descendants"
    ALL = "all"


class StructureType(Enum):
    DATA_STRUCTURE = "datastructure"
    METADATA_STRUCTURE = "metadatastructure"
    CATEGORY_SCHEME = "categoryscheme"
    CONCEPT_SCHEME = "conceptscheme"
    CODELIST = "codelist"
    HIERARCHICAL_CODELIST = "hierarchicalcodelist"
    ORGANISATION_SCHEME = "organisationscheme"
    AGENCY_SCHEME = "agencyscheme"
    DATA_PROVIDER_SCHEME = "dataproviderscheme"
    DATA_CONSUMER_SCHEME = "dataconsumerscheme"
    ORGANISATION_UNIT_SCHEME = "organisationunitscheme"
    DATAFLOW = "dataflow"
    METADATAFLOW = "metadataflow"
    REPORTING_TAXONOMY = "reportingtaxonomy"
    PROVISION_AGREEMENT = "provisionagreement"
    STRUCTURE_SET = "structureset"
    PROCESS = "process"
    CATEGORISATION = "categorisation"
    CONTENT_CONSTRAINT = "contentconstraint"
    ATTACHMENT_CONSTRAINT = "attachmentconstraint"
    ACTUAL_CONSTRAINT = "actualconstraint"
    ALLOWED_CONSTRAINT = "allowedconstraint"
    STRUCTURE = "structure"
    TRANSFORMATION_SCHEME = "transformationscheme"
    RULESET_SCHEME = "rulesetscheme"
    USER_DEFINED_OPERATOR_SCHEME = "userdefinedoperatorscheme"
    CUSTOM_TYPE_SCHEME = "customtypescheme"
    NAME_PERSONALISATION_SCHEME = "namepersonalisationscheme"
    NAME_ALIAS_SCHEME = "namealiasscheme"
    DATA_CONSTRAINT = "dataconstraint"
    METADATA_CONSTRAINT = "metadataconstraint"
    HIERARCHY = "hierarchy"
    HIERARCHY_ASSOCIATION = "hierarchyassociation"
    VTL_MAPPING_SCHEME = "vtlmappingscheme"
    VALUE_LIST = "valuelist"
    STRUCTURE_MAP = "structuremap"
    REPRESENTATION_MAP = "representationmap"
    CONCEPT_SCHEME_MAP = "conceptschememap"
    CATEGORY_SCHEME_MAP = "categoryschememap"
    ORGANISATION_SCHEME_MAP = "organisationschememap"
    REPORTING_TAXONOMY_MAP = "reportingtaxonomymap"
    METADATA_PROVIDER_SCHEME = "metadataproviderscheme"
    METADATA_PROVISION_AGREEMENT = "metadataprovisionagreement"
    ALL = "*"


class StructureFormat(Enum):
    SDMX_ML_2_1_STRUCTURE = "application/vnd.sdmx.structure+xml;version=2.1"
    SDMX_ML_3_0_STRUCTURE = "application/vnd.sdmx.structure+xml;version=3.0.0"
    SDMX_JSON_1_0_0 = "application/vnd.sdmx.structure+json;version=1.0.0"
    SDMX_JSON_2_0_0 = "application/vnd.sdmx.structure+json;version=2.0.0"
    SDMX_JSON = "application/vnd.sdmx.structure+json;version=2.0.0"
    SDMX_EDI = "application/vnd.sdmx.structure+edi;version=1.0"


ITEM_SCHEMES = {
    StructureType.CATEGORY_SCHEME,
    StructureType.CONCEPT_SCHEME,
    StructureType.CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.AGENCY_SCHEME,
    StructureType.DATA_PROVIDER_SCHEME,
    StructureType.METADATA_PROVIDER_SCHEME,
    StructureType.DATA_CONSUMER_SCHEME,
    StructureType.ORGANISATION_UNIT_SCHEME,
    StructureType.REPORTING_TAXONOMY,
    StructureType.TRANSFORMATION_SCHEME,
    StructureType.RULESET_SCHEME,
    StructureType.USER_DEFINED_OPERATOR_SCHEME,
    StructureType.CUSTOM_TYPE_SCHEME,
    StructureType.NAME_PERSONALISATION_SCHEME,
    StructureType.NAME_ALIAS_SCHEME,
    StructureType.VTL_MAPPING_SCHEME,
    StructureType.VALUE_LIST,
    StructureType.HIERARCHICAL_CODELIST,
}

__INITIAL_RESOURCES = {
    StructureType.DATA_STRUCTURE,
    StructureType.METADATA_STRUCTURE,
    StructureType.CATEGORY_SCHEME,
    StructureType.CONCEPT_SCHEME,
    StructureType.CODELIST,
    StructureType.HIERARCHICAL_CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.AGENCY_SCHEME,
    StructureType.DATA_PROVIDER_SCHEME,
    StructureType.DATA_CONSUMER_SCHEME,
    StructureType.ORGANISATION_UNIT_SCHEME,
    StructureType.DATAFLOW,
    StructureType.METADATAFLOW,
    StructureType.REPORTING_TAXONOMY,
    StructureType.PROVISION_AGREEMENT,
    StructureType.STRUCTURE_SET,
    StructureType.PROCESS,
    StructureType.CATEGORISATION,
    StructureType.CONTENT_CONSTRAINT,
    StructureType.ATTACHMENT_CONSTRAINT,
    StructureType.STRUCTURE,
}

__V1_3_RESOURCES = {
    StructureType.ACTUAL_CONSTRAINT,
    StructureType.ALLOWED_CONSTRAINT,
}.union(__INITIAL_RESOURCES)

__V1_5_RESOURCES = {
    StructureType.TRANSFORMATION_SCHEME,
    StructureType.RULESET_SCHEME,
    StructureType.USER_DEFINED_OPERATOR_SCHEME,
    StructureType.CUSTOM_TYPE_SCHEME,
    StructureType.NAME_PERSONALISATION_SCHEME,
    StructureType.NAME_ALIAS_SCHEME,
}.union(__V1_3_RESOURCES)

__V2_0_DEPRECATED = {
    StructureType.HIERARCHICAL_CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.STRUCTURE_SET,
    StructureType.CONTENT_CONSTRAINT,
    StructureType.ATTACHMENT_CONSTRAINT,
    StructureType.ACTUAL_CONSTRAINT,
    StructureType.ALLOWED_CONSTRAINT,
    StructureType.NAME_ALIAS_SCHEME,
}

__V2_0_ADDED = {
    StructureType.DATA_CONSTRAINT,
    StructureType.METADATA_CONSTRAINT,
    StructureType.HIERARCHY,
    StructureType.HIERARCHY_ASSOCIATION,
    StructureType.VTL_MAPPING_SCHEME,
    StructureType.VALUE_LIST,
    StructureType.STRUCTURE_MAP,
    StructureType.REPRESENTATION_MAP,
    StructureType.CONCEPT_SCHEME_MAP,
    StructureType.CATEGORY_SCHEME_MAP,
    StructureType.ORGANISATION_SCHEME_MAP,
    StructureType.REPORTING_TAXONOMY_MAP,
    StructureType.METADATA_PROVIDER_SCHEME,
    StructureType.METADATA_PROVISION_AGREEMENT,
}

__V2_0_RESOURCES = (__V1_5_RESOURCES.difference(__V2_0_DEPRECATED)).union(
    __V2_0_ADDED
)

__API_RESOURCES = {
    "V1.0.0": __INITIAL_RESOURCES,
    "V1.0.1": __INITIAL_RESOURCES,
    "V1.0.2": __INITIAL_RESOURCES,
    "V1.1.0": __INITIAL_RESOURCES,
    "V1.2.0": __INITIAL_RESOURCES,
    "V1.3.0": __V1_3_RESOURCES,
    "V1.4.0": __V1_3_RESOURCES,
    "V1.5.0": __V1_5_RESOURCES,
    "V2.0.0": __V2_0_RESOURCES,
    "V2.1.0": __V2_0_RESOURCES,
    "LATEST": __V2_0_RESOURCES,
}


class StructureQuery(Struct, frozen=True, omit_defaults=True):
    artefact_type: StructureType = StructureType.ALL
    agency_id: str = "*"
    resource_id: str = "*"
    version: str = "~"
    item_id: str = "*"
    detail: StructureDetail = StructureDetail.FULL
    references: StructureReference = StructureReference.NONE


def __check_multiple_items(query: StructureQuery, version: ApiVersion) -> None:
    check_multiple_items(query.agency_id, version)
    check_multiple_items(query.resource_id, version)
    check_multiple_items(query.version, version)
    check_multiple_items(query.item_id, version)
    check_multiple_items(query.agency_id, version)


def __check_artefact_type(artefact_type: str, version: ApiVersion) -> None:
    if "+" in artefact_type:
        artefacts = artefact_type.split("+")
    elif "," in artefact_type:
        artefacts = artefact_type.split(",")
    else:
        artefacts = [artefact_type]
    for a in artefacts:
        if StructureType(a) not in __API_RESOURCES[version.value.label]:
            raise ClientError(
                422,
                "Validation Error",
                f"{a} is not valid for SDMX-REST {version.value}.",
            )


def __check_detail(detail: StructureDetail, version: ApiVersion) -> None:
    if (
        version < ApiVersion.V1_3_0
        and detail
        in [
            "referencepartial",
            "allcompletestubs",
            "referencecompletestubs",
        ]
    ) or (version < ApiVersion.V2_0_0 and detail == "raw"):
        raise ClientError(
            422,
            "Validation Error",
            f"{detail} not allowed in SDMX-REST {version.value}.",
        )


def __check_references(
    references: StructureReference, version: ApiVersion
) -> None:
    pass


def __validate_query(query: StructureQuery, version: ApiVersion) -> None:
    __check_multiple_items(query, version)
    __check_artefact_type(query.artefact_type.value, version)
    __check_detail(query.detail, version)
    __check_references(query.references, version)


def __is_item_allowed(
    artefact_type: StructureType, version: ApiVersion
) -> bool:
    if artefact_type.value in ITEM_SCHEMES and version >= ApiVersion.V1_1_0:
        if (
            version == ApiVersion.V1_1_0
            and artefact_type == StructureType.HIERARCHICAL_CODELIST
        ):
            return False
        else:
            return True
    else:
        return False


def __to_api_eywords(value: str, version: ApiVersion) -> str:
    if value == "*" and version < ApiVersion.V2_0_0:
        return "all"
    elif value == "~" and version < ApiVersion.V2_0_0:
        return "latest"
    elif version < ApiVersion.V2_0_0 and "," in value:
        return value.replace(",", "+")
    else:
        return value


def __create_full_query(query: StructureQuery, version: ApiVersion) -> str:
    url = "/"
    url += "structure/" if version > ApiVersion.V1_5_0 else ""
    res = __to_api_eywords(query.artefact_type.value, version)
    agency = __to_api_eywords(query.agency_id, version)
    id = __to_api_eywords(query.resource_id, version)
    v = __to_api_eywords(query.version, version)
    item = __to_api_eywords(query.item_id, version)
    url += f"{res}/{agency}/{id}/{v}"
    url += (
        f"/{item}" if __is_item_allowed(query.artefact_type, version) else ""
    )
    url += f"?detail={query.detail.value}&references={query.references.value}"
    return url


def get_url(query: StructureQuery, version: ApiVersion) -> str:
    __validate_query(query, version)
    return __create_full_query(query, version)


query = StructureQuery(StructureType.DATAFLOW, "BIS", "CBS")
print(get_url(query, ApiVersion.V1_5_0))
print(get_url(query, ApiVersion.V2_0_0))
