import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConcept
from pysdmx.model import Code, Codelist, Concept, DataType, Facets


@pytest.fixture
def concept():
    return Concept(
        "RATING",
        name="Rating",
        description="Description",
        dtype=DataType.SHORT,
        facets=Facets(min_value=0, max_value=9),
    )


@pytest.fixture
def concept_no_representation():
    return Concept("RATING", name="Rating", description="Description")


@pytest.fixture
def concept_coded_representation():
    code = Code("0")
    cl = Codelist("CL_A", agency="ZZ", version="1.0", items=[code])
    return Concept(
        "RATING",
        name="Rating",
        description="Description",
        codes=cl,
        dtype=DataType.SHORT,
        facets=Facets(min_value=0, max_value=9),
    )


@pytest.fixture
def concept_coded_enum_ref():
    return Concept(
        "RATING",
        name="Rating",
        description="Description",
        enum_ref="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=ZZ:CL_A(1.0)",
        dtype=DataType.SHORT,
        facets=Facets(min_value=0, max_value=9),
    )


@pytest.fixture
def concept_no_name():
    return Concept("RATING")


def test_concept_no_repr(concept_no_representation: Concept):
    sjson = JsonConcept.from_model(concept_no_representation)

    assert sjson.id == concept_no_representation.id
    assert sjson.name == concept_no_representation.name
    assert sjson.description == concept_no_representation.description
    assert len(sjson.annotations) == 0
    assert sjson.coreRepresentation is None
    assert sjson.parent is None
    assert sjson.isoConceptReference is None


def test_concept_repr(concept: Concept):
    sjson = JsonConcept.from_model(concept)

    assert sjson.coreRepresentation is not None
    assert sjson.coreRepresentation.format.dataType == "Short"
    assert sjson.coreRepresentation.format.minValue == 0
    assert sjson.coreRepresentation.format.maxValue == 9


def test_concept_enum_ref(concept_coded_enum_ref: Concept):
    sjson = JsonConcept.from_model(concept_coded_enum_ref)

    assert sjson.coreRepresentation is not None
    assert sjson.coreRepresentation.enumerationFormat.dataType == "Short"
    assert sjson.coreRepresentation.enumerationFormat.minValue == 0
    assert sjson.coreRepresentation.enumerationFormat.maxValue == 9
    assert (
        sjson.coreRepresentation.enumeration == concept_coded_enum_ref.enum_ref
    )


def test_concept_coded(concept_coded_representation: Concept):
    sjson = JsonConcept.from_model(concept_coded_representation)
    expected_cl = (
        "urn:sdmx:org.sdmx.infomodel.codelist."
        f"{concept_coded_representation.codes.short_urn}"
    )

    assert sjson.coreRepresentation is not None
    assert sjson.coreRepresentation.enumeration == expected_cl
    assert sjson.coreRepresentation.enumerationFormat.dataType == "Short"
    assert sjson.coreRepresentation.enumerationFormat.minValue == 0
    assert sjson.coreRepresentation.enumerationFormat.maxValue == 9


def test_concept_no_name(concept_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonConcept.from_model(concept_no_name)
