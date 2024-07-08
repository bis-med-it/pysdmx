from pysdmx.api.qb.structure import StructureType

types_initial = [
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
]

types_1_3_0 = [
    StructureType.ACTUAL_CONSTRAINT,
    StructureType.ALLOWED_CONSTRAINT,
]

types_1_5_0 = [
    StructureType.TRANSFORMATION_SCHEME,
    StructureType.RULESET_SCHEME,
    StructureType.USER_DEFINED_OPERATOR_SCHEME,
    StructureType.CUSTOM_TYPE_SCHEME,
    StructureType.NAME_PERSONALISATION_SCHEME,
    StructureType.NAME_ALIAS_SCHEME,
]

types_2_0_0_deprecated = [
    StructureType.HIERARCHICAL_CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.STRUCTURE_SET,
    StructureType.CONTENT_CONSTRAINT,
    StructureType.ATTACHMENT_CONSTRAINT,
    StructureType.ACTUAL_CONSTRAINT,
    StructureType.ALLOWED_CONSTRAINT,
    StructureType.NAME_ALIAS_SCHEME,
]

types_2_0_0_added = [
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
]

types_2_0_0_all = types_initial.copy()
types_2_0_0_all.extend(types_1_3_0)
types_2_0_0_all.extend(types_1_5_0)
types_2_0_0_all = [
    t for t in types_2_0_0_all if t not in types_2_0_0_deprecated
]
types_2_0_0_all.extend(types_2_0_0_added)
