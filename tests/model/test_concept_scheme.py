from typing import Iterable, Sized

import pytest

from pysdmx.model.concept import Concept, ConceptScheme


@pytest.fixture
def id():
    return "id"


@pytest.fixture
def name():
    return "name"


@pytest.fixture
def agency():
    return "5B0"


def test_defaults(id, name, agency):
    cs = ConceptScheme(id=id, name=name, agency=agency)

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description is None
    assert cs.version == "1.0"
    assert cs.concepts is not None
    assert len(cs.concepts) == 0


def test_full_initialization(id, name, agency):
    desc = "description"
    version = "1.42.0"
    concepts = [Concept(id="child1"), Concept(id="child2")]

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


def test_get_concept(id, name, agency):
    c1 = Concept(id="child1", name="Child 1")
    c2 = Concept(id="child2", name="Child 2")
    concepts = [c1, c2]
    cs = ConceptScheme(id=id, name=name, agency=agency, items=concepts)

    resp1 = cs["child1"]
    resp2 = cs["child3"]

    assert resp1 == c1
    assert "child1" in cs
    assert resp2 is None
    assert "child3" not in cs
