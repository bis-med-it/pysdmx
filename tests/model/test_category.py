from typing import Iterable

import pytest

from pysdmx.model import Category, DataflowRef


@pytest.fixture
def id():
    return "FX"


@pytest.fixture
def name():
    return "Exchange rates"


@pytest.fixture
def desc():
    return "Daily bilateral foreign exchange reference rates"


def test_default(id):
    c = Category(id=id)

    assert c.id == id
    assert c.name is None
    assert c.description is None
    assert c.categories is not None
    assert c.dataflows is not None
    assert len(c.categories) == 0
    assert len(c.dataflows) == 0


def test_full_instantiation(id, name, desc):
    cats = [Category(id="chld", name="Child")]
    flows = [DataflowRef(id="EXR", agency="BIS")]

    c = Category(
        id=id, name=name, description=desc, categories=cats, dataflows=flows
    )

    assert c.id == id
    assert c.name == name
    assert c.description == desc
    assert c.categories == cats
    assert c.dataflows == flows


def test_mutable(id, name):
    """Categories are mutable, so that we can add dataflows to them."""
    c = Category(id=id)
    c.name = name


def test_equal(id, name, desc):
    c1 = Category(id=id, name=name, description=desc)
    c2 = Category(id=id, name=name, description=desc)

    assert c1 == c2


def test_not_equal(id):
    c1 = Category(id=id)
    c2 = Category(id=id + id)

    assert c1 != c2


def test_iterable(id, name):
    cats = [Category(id="chld", name="Child")]
    cat = Category(id=id, name=name, categories=cats)

    assert isinstance(cat, Iterable)
    out = [c.id for c in cat]
    assert len(out) == 1
    assert out == ["chld"]


def test_tostr_id(id):
    c = Category(id=id)

    s = str(c)

    assert s == f"Category(id={id!r})"


def test_tostr_name(id, name):
    c = Category(id=id, name=name)

    s = str(c)

    assert s == f"Category(id={id!r}, name={name!r})"
