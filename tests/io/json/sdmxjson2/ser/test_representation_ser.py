import pytest

from pysdmx.io.json.sdmxjson2.messages.core import JsonRepresentation
from pysdmx.model import ArrayBoundaries, Concept, DataType, Facets


@pytest.fixture
def concept1():
    return Concept(
        "C1",
        dtype=DataType.SHORT,
        facets=Facets(min_value=0, max_value=9),
        enum_ref="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TS:A(1.0)",
    )


@pytest.fixture
def concept2():
    return Concept(
        "C2", dtype=DataType.SHORT, facets=Facets(min_value=0, max_value=9)
    )


@pytest.fixture
def concept3():
    return Concept("C3", dtype=DataType.SHORT)


@pytest.fixture
def concept4():
    return Concept("C4")


def test_enumerated_concept(concept1: Concept):
    sjson = JsonRepresentation.from_model(
        concept1.dtype, concept1.enum_ref, concept1.facets, None
    )

    assert sjson.enumerationFormat.dataType == "Short"
    assert sjson.enumerationFormat.minValue == 0
    assert sjson.enumerationFormat.maxValue == 9
    assert sjson.enumeration == concept1.enum_ref
    assert sjson.format is None
    assert sjson.minOccurs is None
    assert sjson.maxOccurs is None


def test_non_enumerated_concept(concept2: Concept):
    sjson = JsonRepresentation.from_model(
        concept2.dtype, concept2.enum_ref, concept2.facets, None
    )
    assert sjson.enumerationFormat is None
    assert sjson.enumeration is None
    assert sjson.format.dataType == "Short"
    assert sjson.format.minValue == 0
    assert sjson.format.maxValue == 9
    assert sjson.minOccurs is None
    assert sjson.maxOccurs is None


def test_no_facet_concept(concept3: Concept):
    sjson = JsonRepresentation.from_model(
        concept3.dtype, concept3.enum_ref, concept3.facets, None
    )
    assert sjson.enumerationFormat is None
    assert sjson.enumeration is None
    assert sjson.format.dataType == "Short"
    assert sjson.format.minValue is None
    assert sjson.format.maxValue is None
    assert sjson.minOccurs is None
    assert sjson.maxOccurs is None


def test_no_repr_concept(concept4: Concept):
    sjson = JsonRepresentation.from_model(
        concept4.dtype, concept4.enum_ref, concept4.facets, None
    )
    assert sjson is None
