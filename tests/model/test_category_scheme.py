from typing import Iterable, Sized

import msgspec
import pytest

from pysdmx.model.__base import DataflowRef
from pysdmx.model.category import Category, CategoryScheme


@pytest.fixture()
def id():
    return "id"


@pytest.fixture()
def name():
    return "name"


@pytest.fixture()
def agency():
    return "5B0"


@pytest.fixture()
def desc():
    return "description"


@pytest.fixture()
def version():
    return "1.42.0"


@pytest.fixture()
def dataflows():
    df1 = DataflowRef(id="DF1", agency="BIS")
    df2 = DataflowRef(id="DF2", agency="BIS")
    df3 = DataflowRef(id="DF3", agency="BIS")
    df4 = DataflowRef(id="DF4", agency="BIS")
    return [df1, df2, df3, df4]


@pytest.fixture()
def categories(dataflows):

    grandchild = Category(
        id="child211",
        name="Child 2.1.1",
        dataflows=[dataflows[0], dataflows[1]],
    )
    child = Category(
        id="child21",
        name="Child 2.1",
        categories=[grandchild],
        dataflows=[dataflows[2]],
    )
    return [
        Category(id="child1", name="Child 1", dataflows=[dataflows[3]]),
        Category(id="child2", name="Child 2", categories=[child]),
    ]


def test_defaults(id, name, agency):
    cs = CategoryScheme(id=id, name=name, agency=agency)

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description is None
    assert cs.version == "1.0"
    assert cs.categories is not None
    assert len(cs.categories) == 0


def test_full_initialization(id, name, agency, desc, version, categories):

    cs = CategoryScheme(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=categories,
    )

    assert cs.id == id
    assert cs.name == name
    assert cs.agency == agency
    assert cs.description == desc
    assert cs.version == version
    assert cs.categories == categories
    assert len(cs) == 4
    assert len(cs.categories) == 2


def test_immutable(id, name, agency):
    cs = CategoryScheme(id=id, name=name, agency=agency)
    with pytest.raises(AttributeError):
        cs.description = "Description"


def test_iterable(id, name, agency):
    cats = [
        Category(id="child1", name="Child 1"),
        Category(id="child2", name="Child 2"),
    ]
    cs = CategoryScheme(id=id, name=name, agency=agency, items=cats)

    assert isinstance(cs, Iterable)
    out = [c.id for c in cs]
    assert len(out) == 2
    assert out == ["child1", "child2"]


def test_sized(id, name, agency):
    cs = CategoryScheme(id=id, name=name, agency=agency)

    assert isinstance(cs, Sized)


def test_get_category(id, name, agency, categories):
    cs = CategoryScheme(id=id, name=name, agency=agency, items=categories)

    resp1 = cs["child2.child21.child211"]
    resp2 = cs["child2"]
    resp3 = cs["child3"]
    resp4 = cs["child2.child24.child421"]

    assert resp1 == categories[1].categories[0].categories[0]
    assert "child2.child21.child211" in cs
    assert resp2 == categories[1]
    assert "child2" in cs
    assert resp3 is None
    assert "child3" not in cs
    assert resp4 is None
    assert "child2.child24.child421" not in cs


def test_dataflows(id, name, agency, categories, dataflows):

    cs = CategoryScheme(id=id, name=name, agency=agency, items=categories)

    flows = cs.dataflows

    assert len(flows) == 4
    for df in dataflows:
        assert df in flows


def test_serialization(id, name, agency, desc, version, categories):

    cs = CategoryScheme(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=categories,
    )

    ser = msgspec.msgpack.Encoder().encode(cs)

    out = msgspec.msgpack.Decoder(CategoryScheme).decode(ser)

    assert out == cs
