from typing import Iterable, Sized

import pytest

from pysdmx.model.category import Category, CategoryScheme, DataflowRef


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
    cs = CategoryScheme(id, name, agency)

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description is None
    assert cs.version == "1.0"
    assert cs.categories is not None
    assert len(cs.categories) == 0


def test_full_initialization(id, name, agency):
    desc = "description"
    version = "1.42.0"
    grandchild = Category("Child211", "Child 2.1.1")
    child = Category("Child21", "Child 2.1", categories=[grandchild])
    cats = [
        Category("child1", "Child 1"),
        Category("child2", "Child 2", categories=[child]),
    ]

    cs = CategoryScheme(id, name, agency, desc, version, cats)

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description == desc
    assert cs.version == version
    assert cs.categories == cats
    assert len(cs) == 4
    assert len(cs.categories) == 2


def test_immutable(id, name, agency):
    cs = CategoryScheme(id, name, agency)
    with pytest.raises(AttributeError):
        cs.description = "Description"


def test_iterable(id, name, agency):
    cats = [
        Category("child1", "Child 1"),
        Category("child2", "Child 2"),
    ]
    cs = CategoryScheme(id, name, agency, categories=cats)

    assert isinstance(cs, Iterable)
    out = [c.id for c in cs]
    assert len(out) == 2
    assert out == ["child1", "child2"]


def test_sized(id, name, agency):
    cs = CategoryScheme(id, name, agency)

    assert isinstance(cs, Sized)


def test_get_category(id, name, agency):
    grandchild = Category("child211", "Child 2.1.1")
    child = Category("child21", "Child 2.1", categories=[grandchild])
    cats = [
        Category("child1", "Child 1"),
        Category("child2", "Child 2", categories=[child]),
    ]

    cs = CategoryScheme(id, name, agency, categories=cats)

    resp1 = cs["child2.child21.child211"]
    resp2 = cs["child2"]
    resp3 = cs["child3"]
    resp4 = cs["child2.child24.child421"]

    assert resp1 == grandchild
    assert resp2 == cats[1]
    assert resp3 is None
    assert resp4 is None


def test_dataflows(id, name, agency):
    df1 = DataflowRef("DF1", "BIS")
    df2 = DataflowRef("DF2", "BIS")
    df3 = DataflowRef("DF3", "BIS")
    df4 = DataflowRef("DF4", "BIS")

    grandchild = Category("child211", "Child 2.1.1", dataflows=[df1, df2])
    child = Category(
        "child21", "Child 2.1", categories=[grandchild], dataflows=[df3]
    )
    cats = [
        Category("child1", "Child 1", dataflows=[df4]),
        Category("child2", "Child 2", categories=[child]),
    ]

    cs = CategoryScheme(id, name, agency, categories=cats)

    flows = cs.dataflows

    assert len(flows) == 4
    assert df1 in flows
    assert df2 in flows
    assert df3 in flows
    assert df4 in flows
