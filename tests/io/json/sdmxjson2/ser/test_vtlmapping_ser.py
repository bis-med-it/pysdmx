import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.vtl import JsonVtlMapping
from pysdmx.model import Codelist, Concept
from pysdmx.model.__base import DataflowRef, ItemReference, Reference
from pysdmx.model.vtl import (
    FromVtlMapping,
    ToVtlMapping,
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
    VtlMapping,
)

_BASE = "urn:sdmx:org.sdmx.infomodel."


@pytest.fixture
def vtl_codelist_mapping():
    return VtlCodelistMapping(
        "CODELIST_MAP",
        name="Codelist Mapping",
        description="Description",
        codelist="CL_FREQ",
        codelist_alias="FREQ",
    )


@pytest.fixture
def vtl_codelist_mapping_with_object():
    codelist = Codelist(
        "CL_FREQ", name="Frequency", agency="BIS", version="1.0"
    )
    return VtlCodelistMapping(
        "CODELIST_MAP",
        name="Codelist Mapping",
        description="Description",
        codelist=codelist,
        codelist_alias="FREQ",
    )


@pytest.fixture
def vtl_codelist_mapping_with_reference():
    codelist_ref = Reference(
        sdmx_type="Codelist", id="CL_FREQ", agency="BIS", version="1.0"
    )
    return VtlCodelistMapping(
        "CODELIST_MAP",
        name="Codelist Mapping",
        description="Description",
        codelist=codelist_ref,
        codelist_alias="FREQ",
    )


@pytest.fixture
def vtl_concept_mapping():
    return VtlConceptMapping(
        "CONCEPT_MAP",
        name="Concept Mapping",
        description="Description",
        concept="FREQ",
        concept_alias="FREQUENCY",
    )


@pytest.fixture
def vtl_concept_mapping_with_concept():
    concept = Concept(
        "FREQ",
        name="Frequency",
        urn=f"{_BASE}conceptscheme.Concept=BIS:BIS_CONCEPTS(1.0).FREQ",
    )
    return VtlConceptMapping(
        "CONCEPT_MAP",
        name="Concept Mapping",
        description="Description",
        concept=concept,
        concept_alias="FREQUENCY",
    )


@pytest.fixture
def vtl_concept_mapping_with_reference():
    concept_ref = ItemReference(
        sdmx_type="Concept",
        id="BIS_CONCEPTS",
        agency="BIS",
        version="1.0",
        item_id="FREQ",
    )
    return VtlConceptMapping(
        "CONCEPT_MAP",
        name="Concept Mapping",
        description="Description",
        concept=concept_ref,
        concept_alias="FREQUENCY",
    )


@pytest.fixture
def vtl_concept_mapping_with_concept_no_urn():
    concept = Concept("FREQ", name="Frequency")
    return VtlConceptMapping(
        "CONCEPT_MAP",
        name="Concept Mapping",
        description="Description",
        concept=concept,
        concept_alias="FREQUENCY",
    )


@pytest.fixture
def vtl_dataflow_mapping():
    return VtlDataflowMapping(
        "DATAFLOW_MAP",
        name="Dataflow Mapping",
        description="Description",
        dataflow=DataflowRef(id="DF1", agency="BIS", version="1.0"),
        dataflow_alias="DF_ALIAS",
        to_vtl_mapping_method=ToVtlMapping(["sub1", "sub2"], "to_type"),
        from_vtl_mapping_method=FromVtlMapping(
            ["super1", "super2"], "from_type"
        ),
    )


@pytest.fixture
def vtl_codelist_mapping_no_name():
    return VtlCodelistMapping(
        "CODELIST_MAP",
        codelist="CL_FREQ",
        codelist_alias="FREQ",
    )


@pytest.fixture
def unsupported_type():
    # Create a mock VtlMapping that's not one of the supported types
    class UnsupportedVtlMapping(VtlMapping):
        """Just an unsupported type."""

    return UnsupportedVtlMapping("TEST", name="Test name")


def test_vtl_codelist_mapping(vtl_codelist_mapping: VtlCodelistMapping):
    sjson = JsonVtlMapping.from_model(vtl_codelist_mapping)

    assert sjson.id == vtl_codelist_mapping.id
    assert sjson.name == vtl_codelist_mapping.name
    assert sjson.description == vtl_codelist_mapping.description
    assert sjson.alias == vtl_codelist_mapping.codelist_alias
    assert sjson.codelist == vtl_codelist_mapping.codelist
    assert sjson.concept is None
    assert sjson.dataflow is None


def test_vtl_codelist_mapping_with_object(
    vtl_codelist_mapping_with_object: VtlCodelistMapping,
):
    sjson = JsonVtlMapping.from_model(vtl_codelist_mapping_with_object)

    assert sjson.codelist == f"{_BASE}codelist.Codelist=BIS:CL_FREQ(1.0)"


def test_vtl_codelist_mapping_with_reference(
    vtl_codelist_mapping_with_reference: VtlCodelistMapping,
):
    sjson = JsonVtlMapping.from_model(vtl_codelist_mapping_with_reference)

    assert sjson.codelist == f"{_BASE}codelist.Codelist=BIS:CL_FREQ(1.0)"


def test_vtl_concept_mapping(vtl_concept_mapping: VtlConceptMapping):
    sjson = JsonVtlMapping.from_model(vtl_concept_mapping)

    assert sjson.id == vtl_concept_mapping.id
    assert sjson.name == vtl_concept_mapping.name
    assert sjson.description == vtl_concept_mapping.description
    assert sjson.alias == vtl_concept_mapping.concept_alias
    assert sjson.concept == vtl_concept_mapping.concept
    assert sjson.codelist is None
    assert sjson.dataflow is None


def test_vtl_concept_mapping_with_object(
    vtl_concept_mapping_with_concept: VtlConceptMapping,
):
    sjson = JsonVtlMapping.from_model(vtl_concept_mapping_with_concept)

    assert (
        sjson.concept
        == f"{_BASE}conceptscheme.Concept=BIS:BIS_CONCEPTS(1.0).FREQ"
    )


def test_vtl_concept_mapping_with_reference(
    vtl_concept_mapping_with_reference: VtlConceptMapping,
):
    sjson = JsonVtlMapping.from_model(vtl_concept_mapping_with_reference)

    assert (
        sjson.concept
        == f"{_BASE}conceptscheme.Concept=BIS:BIS_CONCEPTS(1.0).FREQ"
    )


def test_vtl_dataflow_mapping(vtl_dataflow_mapping: VtlDataflowMapping):
    sjson = JsonVtlMapping.from_model(vtl_dataflow_mapping)

    assert sjson.id == vtl_dataflow_mapping.id
    assert sjson.name == vtl_dataflow_mapping.name
    assert sjson.description == vtl_dataflow_mapping.description
    assert sjson.alias == vtl_dataflow_mapping.dataflow_alias
    assert sjson.dataflow == f"{_BASE}datastructure.Dataflow=BIS:DF1(1.0)"
    assert sjson.concept is None
    assert sjson.codelist is None
    assert sjson.toVtlMapping is not None
    assert sjson.fromVtlMapping is not None


def test_vtl_mapping_no_name(vtl_codelist_mapping_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonVtlMapping.from_model(vtl_codelist_mapping_no_name)


def test_unsupported_type(unsupported_type):
    with pytest.raises(errors.Invalid, match="Unsupported VTL mapping type"):
        JsonVtlMapping.from_model(unsupported_type)


def test_concept_without_urn(vtl_concept_mapping_with_concept_no_urn):
    with pytest.raises(errors.Invalid, match="Missing concept reference"):
        JsonVtlMapping.from_model(vtl_concept_mapping_with_concept_no_urn)
