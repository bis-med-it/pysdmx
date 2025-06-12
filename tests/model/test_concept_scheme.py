from typing import Iterable, Sized

import msgspec
import pytest

from pysdmx.model.concept import Concept, ConceptScheme, DataType, Facets


@pytest.fixture
def id():
    return "id"


@pytest.fixture
def name():
    return "name"


@pytest.fixture
def agency():
    return "5B0"


@pytest.fixture
def desc():
    return "description"


@pytest.fixture
def version():
    return "1.42.0"


@pytest.fixture
def concepts():
    return [
        Concept(
            id="child1",
            name="Test",
            description="desc",
            dtype=DataType.ALPHA,
            facets=Facets(min_length=1, max_length=3),
        ),
        Concept(id="child2"),
    ]


def test_defaults(id, name, agency):
    cs = ConceptScheme(id=id, name=name, agency=agency)

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description is None
    assert cs.version == "1.0"
    assert cs.concepts is not None
    assert len(cs.concepts) == 0


def test_full_initialization(id, name, agency, desc, version, concepts):
    cs = ConceptScheme(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=concepts,
    )

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description == desc
    assert cs.version == version
    assert cs.concepts == concepts
    assert len(cs) == 2
    assert len(cs) == len(cs.concepts)


def test_immutable(id, name, agency):
    cs = ConceptScheme(id=id, name=name, agency=agency)
    with pytest.raises(AttributeError):
        cs.description = "Description"


def test_iterable(id, name, agency):
    concepts = [Concept(id="child1"), Concept(id="child2")]
    cs = ConceptScheme(id=id, name=name, agency=agency, items=concepts)

    assert isinstance(cs, Iterable)
    out = [c.id for c in cs]
    assert len(out) == 2
    assert out == ["child1", "child2"]


def test_sized(id, name, agency):
    cs = ConceptScheme(id=id, name=name, agency=agency)

    assert isinstance(cs, Sized)


def test_get_concept(id, name, agency, concepts):
    cs = ConceptScheme(id=id, name=name, agency=agency, items=concepts)

    resp1 = cs["child1"]
    resp2 = cs["child3"]

    assert resp1 == concepts[0]
    assert "child1" in cs
    assert resp2 is None


def test_serialization(id, name, agency, desc, version, concepts):
    cs = ConceptScheme(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=concepts,
    )

    ser = msgspec.msgpack.Encoder().encode(cs)

    out = msgspec.msgpack.Decoder(ConceptScheme).decode(ser)

    assert out == cs


def test_conceptscheme_str(id, name, agency, desc, version, concepts):
    concept_scheme = ConceptScheme(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=concepts,
    )

    s = str(concept_scheme)
    expected_str = (
        "id: id, "
        "name: name, "
        "description: description, "
        "version: 1.42.0, "
        "agency: 5B0, "
        "items: 2 concepts"
    )
    assert s == expected_str


def test_conceptscheme_repr(id, name, agency, desc, version, concepts):
    concept_scheme = ConceptScheme(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=concepts,
    )

    r = repr(concept_scheme)
    expected_repr = (
        "ConceptScheme("
        "id='id', "
        "name='name', "
        "description='description', "
        "version='1.42.0', "
        "agency='5B0', "
        "items=["
        "Concept("
        "id='child1', "
        "name='Test', "
        "description='desc', "
        "dtype=DataType.ALPHA, "
        "facets=Facets(min_length=1, max_length=3)), "
        "Concept(id='child2')])"
    )
    assert r == expected_repr
