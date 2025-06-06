from datetime import datetime, timezone
from typing import Iterable

import pytest

from pysdmx.model import HierarchicalCode


@pytest.fixture
def id():
    return "UY"


@pytest.fixture
def name():
    return "Uruguay"


@pytest.fixture
def desc():
    return "The Oriental Republic of Uruguay"


@pytest.fixture
def vf():
    return datetime(1828, 8, 27, 0, 0, 0, tzinfo=timezone.utc)


@pytest.fixture
def vt():
    return None


@pytest.fixture
def child_codes():
    return [
        HierarchicalCode(id="child1", name="Child 1"),
        HierarchicalCode(id="child2", name="Child 2"),
    ]


def test_default(id):
    c = HierarchicalCode(id)

    assert c.id == id
    assert c.name is None
    assert c.description is None
    assert c.valid_from is None
    assert c.valid_to is None


def test_full_instantiation(id, name, desc, vf, vt):
    c = HierarchicalCode(id, name, desc, vf, vt)

    assert c.id == id
    assert c.name == name
    assert c.description == desc
    assert c.valid_from == vf
    assert c.valid_to == vt


def test_immutable(id, name):
    c = HierarchicalCode(id)
    with pytest.raises(AttributeError):
        c.name = name


def test_equal(id, name, desc):
    c1 = HierarchicalCode(id, name, desc)
    c2 = HierarchicalCode(id, name, desc)

    assert c1 == c2


def test_not_equal(id):
    c1 = HierarchicalCode(id)
    c2 = HierarchicalCode(id + id)

    assert c1 != c2


def test_iterable(id, name):
    codes = [HierarchicalCode("chld", "Child")]
    hc = HierarchicalCode(id, name, codes=codes)

    assert isinstance(hc, Iterable)
    out = [c.id for c in hc]
    assert len(out) == 1
    assert out == ["chld"]


def test_tostr_id(id):
    hc = HierarchicalCode(id=id)

    s = str(hc)
    expected_str = f"id: {id}"

    assert s == expected_str


def test_tostr_name(id, name):
    hc = HierarchicalCode(id=id, name=name, codes=[])

    s = str(hc)
    expected_str = f"id: {id}, name: {name}"

    assert s == expected_str


def test_tostr_full(id, name, desc, vf, vt, child_codes):
    hc = HierarchicalCode(
        id=id,
        name=name,
        description=desc,
        valid_from=vf,
        valid_to=vt,
        codes=child_codes,
    )

    s = str(hc)
    expected_str = (f"id: {id}, name: {name}, description: {desc}, "
                    f"valid_from: {vf}, codes: 2 hierarchicalcodes")

    assert s == expected_str


def test_torepr_id(id):
    hc = HierarchicalCode(id=id)

    r = repr(hc)
    expected_repr = f"HierarchicalCode(id='{id}')"

    assert r == expected_repr


def test_torepr_full(id, name, desc, vf, vt, child_codes):
    hc = HierarchicalCode(
        id=id,
        name=name,
        description=desc,
        valid_from=vf,
        valid_to=vt,
        codes=child_codes,
    )

    r = repr(hc)
    expected_repr = (
        f"HierarchicalCode(id='{id}', "
        f"name='{name}', "
        f"description='{desc}', "
        f"valid_from={vf!r}, "
        f"codes=[HierarchicalCode(id='child1', name='Child 1'), "
        f"HierarchicalCode(id='child2', name='Child 2')])"
    )

    assert r == expected_repr


def test_torepr_empty(id, name, desc, vf, vt):
    hc = HierarchicalCode(
        id=id,
        name=name,
        description=desc,
        valid_from=vf,
        valid_to=vt,
        codes=[],
    )

    r = repr(hc)
    expected_repr = (
        f"HierarchicalCode(id='{id}', "
        f"name='{name}', "
        f"description='{desc}', "
        f"valid_from={vf!r})"
    )

    assert r == expected_repr
