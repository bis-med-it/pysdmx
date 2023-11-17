from typing import Iterable, Sized

import pytest

from pysdmx.model import HierarchicalCode, Hierarchy


@pytest.fixture()
def id():
    return "id"


@pytest.fixture()
def name():
    return "name"


@pytest.fixture()
def agency():
    return "5B0"


def test_defaults(id, name, agency):
    cs = Hierarchy(id, name, agency)

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description is None
    assert cs.version == "1.0"
    assert cs.codes is not None
    assert len(cs.codes) == 0


def test_full_initialization(id, name, agency):
    desc = "description"
    version = "1.42.0"
    grandchild = HierarchicalCode("Child211", "Child 2.1.1")
    child = HierarchicalCode("Child21", "Child 2.1", codes=[grandchild])
    codes = [
        HierarchicalCode("child1", "Child 1"),
        HierarchicalCode("child2", "Child 2", codes=[child]),
    ]

    cs = Hierarchy(id, name, agency, desc, version, codes)

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description == desc
    assert cs.version == version
    assert cs.codes == codes
    assert len(cs) == 4
    assert len(cs.codes) == 2


def test_immutable(id, name, agency):
    cs = Hierarchy(id, name, agency)
    with pytest.raises(AttributeError):
        cs.description = "Description"


def test_iterable(id, name, agency):
    codes = [
        HierarchicalCode("child1", "Child 1"),
        HierarchicalCode("child2", "Child 2"),
    ]
    cs = Hierarchy(id, name, agency, codes=codes)

    assert isinstance(cs, Iterable)
    out = [c.id for c in cs]
    assert len(out) == 2
    assert out == ["child1", "child2"]


def test_sized(id, name, agency):
    cs = Hierarchy(id, name, agency)

    assert isinstance(cs, Sized)


def test_get_code(id, name, agency):
    grandchild = HierarchicalCode("child211", "Child 2.1.1")
    child = HierarchicalCode("child21", "Child 2.1", codes=[grandchild])
    codes = [
        HierarchicalCode("child1", "Child 1"),
        HierarchicalCode("child2", "Child 2", codes=[child]),
    ]

    cs = Hierarchy(id, name, agency, codes=codes)

    resp1 = cs["child2.child21.child211"]
    resp2 = cs["child2"]
    resp3 = cs["child3"]
    resp4 = cs["child2.child24.child421"]

    assert resp1 == grandchild
    assert resp2 == codes[1]
    assert resp3 is None
    assert resp4 is None
