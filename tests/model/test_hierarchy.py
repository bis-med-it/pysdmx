from typing import Iterable, Sized

import msgspec
import pytest

from pysdmx.model import HierarchicalCode, Hierarchy


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
def operator():
    return (
        "urn:sdmx:org.sdmx.infomodel.transformation."
        "UserDefinedOperator=SDMX:OPS(1.0).SUM"
    )


@pytest.fixture
def desc():
    return "description"


@pytest.fixture
def version():
    return "1.42.0"


@pytest.fixture
def codes():
    grandchild = HierarchicalCode("child211", "Child 2.1.1")
    child = HierarchicalCode("child21", "Child 2.1", codes=[grandchild])
    return [
        HierarchicalCode("child1", "Child 1"),
        HierarchicalCode("child2", "Child 2", codes=[child]),
    ]


def test_defaults(id, name, agency):
    cs = Hierarchy(id=id, name=name, agency=agency)

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description is None
    assert cs.version == "1.0"
    assert cs.codes is not None
    assert len(cs.codes) == 0
    assert cs.operator is None


def test_full_initialization(id, name, agency, operator, desc, version, codes):
    cs = Hierarchy(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        codes=codes,
        operator=operator,
    )

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description == desc
    assert cs.version == version
    assert cs.codes == codes
    assert len(cs) == 4
    assert len(cs.codes) == 2
    assert cs.operator == operator


def test_immutable(id, name, agency):
    cs = Hierarchy(id=id, name=name, agency=agency)
    with pytest.raises(AttributeError):
        cs.description = "Description"


def test_iterable(id, name, agency, codes):
    cs = Hierarchy(id=id, name=name, agency=agency, codes=codes)

    assert isinstance(cs, Iterable)
    assert len(cs) == 4


def test_sized(id, name, agency):
    cs = Hierarchy(id=id, name=name, agency=agency)

    assert isinstance(cs, Sized)


def test_get_code(id, name, agency, codes):
    cs = Hierarchy(id=id, name=name, agency=agency, codes=codes)

    resp1 = cs["child2.child21.child211"]
    resp2 = cs["child2"]
    resp3 = cs["child3"]
    resp4 = cs["child2.child24.child421"]

    assert resp1 == codes[1].codes[0].codes[0]
    assert "child2.child21.child211" in cs
    assert resp2 == codes[1]
    assert "child2" in cs
    assert resp3 is None
    assert "child3" not in cs
    assert resp4 is None
    assert "child2.child24.child421" not in cs


def test_codes_by_id_no_parent_needed(id, name, agency, codes):
    cs = Hierarchy(id=id, name=name, agency=agency, codes=codes)

    m = cs.by_id("child211")

    assert isinstance(m, Iterable)
    assert len(m) == 1
    m = list(m)
    assert m[0] == codes[1].codes[0].codes[0]


def test_codes_by_id_is_a_set(id, name, agency):
    grandchild1 = HierarchicalCode("child211", "Child 2.1.1")
    grandchild2 = HierarchicalCode("child212", "Child 2.1.2")
    child1 = HierarchicalCode(
        "child21", "Child 2.1", codes=[grandchild1, grandchild2]
    )
    child2 = HierarchicalCode("child22", "Child 2.2", codes=[grandchild1])
    codes = [
        HierarchicalCode("child1", "Child 1"),
        HierarchicalCode("child2", "Child 2", codes=[child1, child2]),
    ]
    cs = Hierarchy(id=id, name=name, agency=agency, codes=codes)

    m = cs.by_id("child211")

    assert isinstance(m, Iterable)
    assert len(m) == 1
    m = list(m)
    assert m[0] == grandchild1


def test_codes_by_id_diff_names(id, name, agency):
    grandchild1 = HierarchicalCode("child211", "Child 2.1.1")
    grandchild2 = HierarchicalCode("child212", "Child 2.1.2")
    grandchild3 = HierarchicalCode("child211", "Child 2.1.1 - Diff name")
    child1 = HierarchicalCode(
        "child21", "Child 2.1", codes=[grandchild1, grandchild2]
    )
    child2 = HierarchicalCode("child22", "Child 2.2", codes=[grandchild3])
    codes = [
        HierarchicalCode("child1", "Child 1"),
        HierarchicalCode("child2", "Child 2", codes=[child1, child2]),
    ]
    cs = Hierarchy(id=id, name=name, agency=agency, codes=codes)

    m = cs.by_id("child211")

    assert isinstance(m, Iterable)
    assert len(m) == 2
    m = list(m)
    assert grandchild1 in m
    assert grandchild3 in m


def test_all_codes(id, name, agency):
    grandchild1 = HierarchicalCode("grandchild1", "grandchild 1")
    grandchild2 = HierarchicalCode("grandchild2", "grandchild 2")
    grandchild3 = HierarchicalCode("grandchild3", "grandchild 3")
    child1 = HierarchicalCode(
        "child1", "child 1", codes=[grandchild1, grandchild2]
    )
    child2 = HierarchicalCode(
        "child2", "child 2", codes=[grandchild1, grandchild2, grandchild3]
    )
    parent1 = HierarchicalCode("parent1", "parent 1")
    parent2 = HierarchicalCode(
        "parent2",
        "parent 2",
        codes=[child1, child2],
    )

    h = Hierarchy(id=id, name=name, agency=agency, codes=[parent1, parent2])

    m = h.all_codes()
    assert len(m) == 7


def test_serialization(id, name, agency, operator, desc, version, codes):
    h = Hierarchy(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        codes=codes,
        operator=operator,
    )

    ser = msgspec.msgpack.Encoder().encode(h)

    out = msgspec.msgpack.Decoder(Hierarchy).decode(ser)

    assert out == h


def test_hierarchy_str(id, name, agency, operator, desc, version, codes):
    hierarchy = Hierarchy(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        codes=codes,
        operator=operator,
    )

    s = str(hierarchy)
    expected_str = (
        f"id: {id}, name: {name}, description: {desc}, version: {version}, "
        f"agency: {agency}, codes: 2 hierarchicalcodes, operator: {operator}"
    )
    assert s == expected_str


def test_hierarchy_repr(id, name, agency, operator, desc, version, codes):
    hierarchy = Hierarchy(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        codes=codes,
        operator=operator,
    )

    r = repr(hierarchy)
    expected_repr = (
        "Hierarchy("
        "id='id', "
        "name='name', "
        "description='description', "
        "version='1.42.0', "
        "agency='5B0', "
        "codes=["
        "HierarchicalCode(id='child1', name='Child 1'), "
        "HierarchicalCode(id='child2', name='Child 2', "
        "codes=["
        "HierarchicalCode(id='child21', name='Child 2.1', "
        "codes=["
        "HierarchicalCode(id='child211', name='Child 2.1.1')])])"
        "], "
        "operator='urn:sdmx:org.sdmx.infomodel.transformation.UserDefinedOperator=SDMX:OPS(1.0).SUM')"
    )
    assert r == expected_repr
