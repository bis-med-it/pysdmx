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
    c = HierarchicalCode(id)

    s = str(c)

    assert s == id


def test_tostr_name(id, name):
    c = HierarchicalCode(id, name)

    s = str(c)

    assert s == f"{id} ({name})"
