from pysdmx.api.qb.structure import ITEM_SCHEMES, StructureType


def test_expected_types():
    expected = [
        "datastructure",
        "metadatastructure",
        "categoryscheme",
        "conceptscheme",
        "codelist",
        "hierarchicalcodelist",
        "organisationscheme",
        "agencyscheme",
        "dataproviderscheme",
        "dataconsumerscheme",
        "organisationunitscheme",
        "dataflow",
        "metadataflow",
        "reportingtaxonomy",
        "provisionagreement",
        "structureset",
        "process",
        "categorisation",
        "contentconstraint",
        "attachmentconstraint",
        "actualconstraint",
        "allowedconstraint",
        "transformationscheme",
        "rulesetscheme",
        "userdefinedoperatorscheme",
        "customtypescheme",
        "namepersonalisationscheme",
        "namealiasscheme",
        "dataconstraint",
        "metadataconstraint",
        "hierarchy",
        "hierarchyassociation",
        "vtlmappingscheme",
        "valuelist",
        "structuremap",
        "representationmap",
        "conceptschememap",
        "categoryschememap",
        "organisationschememap",
        "reportingtaxonomymap",
        "metadataproviderscheme",
        "metadataprovisionagreement",
        "*",
    ]

    assert len(StructureType) == len(expected)
    for st in StructureType:
        assert st.value in expected


def test_item_schemes():
    expected = [
        "categoryscheme",
        "conceptscheme",
        "codelist",
        "hierarchicalcodelist",
        "organisationscheme",
        "agencyscheme",
        "dataproviderscheme",
        "dataconsumerscheme",
        "organisationunitscheme",
        "reportingtaxonomy",
        "transformationscheme",
        "rulesetscheme",
        "userdefinedoperatorscheme",
        "customtypescheme",
        "namepersonalisationscheme",
        "namealiasscheme",
        "vtlmappingscheme",
        "valuelist",
        "metadataproviderscheme",
    ]

    assert len(ITEM_SCHEMES) == len(expected)
    for st in ITEM_SCHEMES:
        assert st.value in expected
