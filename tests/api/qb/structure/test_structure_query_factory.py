import pytest

from pysdmx.api.qb.structure import (
    REST_ALL,
    REST_LATEST,
    StructureQuery,
    StructureType,
)
from pysdmx.errors import Invalid
from pysdmx.model import ItemReference, Reference


@pytest.fixture
def maintainable_ref() -> Reference:
    return Reference("Codelist", "SDMX", "CL_FREQ", "2.1")


@pytest.fixture
def unknown_ref() -> Reference:
    return Reference("xxx", "SDMX", "REP_TAX", "2.1")


@pytest.fixture
def code_ref() -> ItemReference:
    return ItemReference("Code", "SDMX", "CL_FREQ", "2.1", "A")


@pytest.fixture
def concept_ref() -> ItemReference:
    return ItemReference("Concept", "SDMX", "CROSS_DOMAIN", "2.0", "FREQ")


@pytest.fixture
def rep_ref() -> ItemReference:
    return ItemReference("reportingcategory", "SDMX", "REP_TAX", "2.1", "CAT1")


@pytest.fixture
def unknown_item_ref() -> ItemReference:
    return ItemReference("xxx", "SDMX", "REP_TAX", "2.1", "CAT1")


def test_maintainable_ref(maintainable_ref: Reference):
    q = StructureQuery.from_ref(maintainable_ref)

    assert isinstance(q, StructureQuery)
    assert q.artefact_type == StructureType.CODELIST
    assert q.agency_id == maintainable_ref.agency
    assert q.resource_id == maintainable_ref.id
    assert q.version == maintainable_ref.version


def test_unknown_maintainable_ref(unknown_ref: Reference):
    with pytest.raises(Invalid):
        StructureQuery.from_ref(unknown_ref)


def test_item_query_code(code_ref: ItemReference):
    q = StructureQuery.from_ref(code_ref)

    assert isinstance(q, StructureQuery)
    assert q.artefact_type == StructureType.CODELIST
    assert q.agency_id == code_ref.agency
    assert q.resource_id == code_ref.id
    assert q.version == code_ref.version
    assert q.item_id == code_ref.item_id


def test_item_query_rep_cat(rep_ref: ItemReference):
    q = StructureQuery.from_ref(rep_ref)

    assert isinstance(q, StructureQuery)
    assert q.artefact_type == StructureType.REPORTING_TAXONOMY
    assert q.agency_id == rep_ref.agency
    assert q.resource_id == rep_ref.id
    assert q.version == rep_ref.version
    assert q.item_id == rep_ref.item_id


def test_item_query_concept(concept_ref: ItemReference):
    q = StructureQuery.from_ref(concept_ref)

    assert isinstance(q, StructureQuery)
    assert q.artefact_type == StructureType.CONCEPT_SCHEME
    assert q.agency_id == concept_ref.agency
    assert q.resource_id == concept_ref.id
    assert q.version == concept_ref.version
    assert q.item_id == concept_ref.item_id


def test_unknown_ref(unknown_item_ref: ItemReference):
    with pytest.raises(Invalid):
        StructureQuery.from_ref(unknown_item_ref)


__base_urn = "urn:sdmx:org.sdmx.infomodel."
maintainable_urns = [
    (
        f"{__base_urn}datastructure.DataStructure=ESTAT:CPI(2.1.0)",
        StructureType.DATA_STRUCTURE,
    ),
    (
        f"{__base_urn}datastructure.Dataflow=ESTAT:BPM6_BOP_M(2.4.0)",
        StructureType.DATAFLOW,
    ),
    (
        f"{__base_urn}registry.DataConstraint=IAEG-SDGs:CN_SDG_GLC(1.20)",
        StructureType.DATA_CONSTRAINT,
    ),
    (
        f"{__base_urn}base.AgencyScheme=SDMX:AGENCIES(1.0)",
        StructureType.AGENCY_SCHEME,
    ),
    (
        f"{__base_urn}codelist.Codelist=ESTAT:CL_ACTIVITY(1.11.0)",
        StructureType.CODELIST,
    ),
    (
        f"{__base_urn}codelist.Hierarchy=ESTAT:HCL_WSTATUS_SCL_BNSPART(1.0)",
        StructureType.HIERARCHY,
    ),
    (
        f"{__base_urn}conceptscheme.ConceptScheme=ESTAT:CS_NA(1.17.0)",
        StructureType.CONCEPT_SCHEME,
    ),
    (
        f"{__base_urn}categoryscheme.CategoryScheme=ESTAT:ESA2010TP(1.0)",
        StructureType.CATEGORY_SCHEME,
    ),
]


@pytest.mark.parametrize(("urn", "expected_type"), maintainable_urns)
def test_from_maintainable_urn(urn, expected_type):
    q = StructureQuery.from_ref(urn)

    assert isinstance(q, StructureQuery)
    assert q.artefact_type == expected_type
    assert q.agency_id != REST_ALL
    assert q.resource_id != REST_ALL
    assert q.version != REST_LATEST
    assert q.item_id is None


item_urns = [
    (
        f"{__base_urn}categoryscheme.Category=ESTAT:ESA2010TP(1.0).ESA2010MA",
        StructureType.CATEGORY_SCHEME,
    ),
    (
        f"{__base_urn}conceptscheme.Concept=ESTAT:CS_NA(1.17.0).FREQ",
        StructureType.CONCEPT_SCHEME,
    ),
    (
        f"{__base_urn}codelist.Code=ESTAT:CL_ACTIVITY(1.11.0).A",
        StructureType.CODELIST,
    ),
    (
        f"{__base_urn}codelist.HierarchicalCode=ESTAT:TEST(1.0).thUA",
        StructureType.HIERARCHY,
    ),
    (
        f"{__base_urn}.base.Agency=SDMX:AGENCIES(1.0).ILO",
        StructureType.AGENCY_SCHEME,
    ),
    (
        f"{__base_urn}.base.DataProvider=ESTAT:DATA_PROVIDERS(1.0).OECD",
        StructureType.DATA_PROVIDER_SCHEME,
    ),
]


@pytest.mark.parametrize(("urn", "expected_type"), item_urns)
def test_from_item_urn(urn, expected_type):
    q = StructureQuery.from_ref(urn)

    assert isinstance(q, StructureQuery)
    assert q.artefact_type == expected_type
    assert q.agency_id != REST_ALL
    assert q.resource_id != REST_ALL
    assert q.version != REST_LATEST
    assert q.item_id is not None
