from typing import Iterable, Sized

import pytest

from pysdmx.model.code import Code, Codelist


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
def sdmx_type():
    return "valuelist"


def test_defaults(id, name, agency):
    cl = Codelist(id=id, name=name, agency=agency)

    assert cl.id == id
    assert cl.name == name
    assert cl.agency == agency
    assert cl.description is None
    assert cl.version == "1.0"
    assert cl.codes is not None
    assert len(cl.codes) == 0
    assert cl.sdmx_type == "codelist"


def test_full_initialization(id, name, agency, sdmx_type):
    desc = "description"
    version = "1.42.0"
    codes = [
        Code(id="child1", name="Child 1"),
        Code(id="child2", name="Child 2"),
    ]

    cl = Codelist(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        items=codes,
        sdmx_type=sdmx_type,
    )

    assert cl.id == id
    assert cl.name == name
    assert cl.agency == agency
    assert cl.description == desc
    assert cl.version == version
    assert cl.codes == codes
    assert len(cl) == 2
    assert len(cl) == len(cl.codes)
    assert cl.sdmx_type == sdmx_type


def test_immutable(id, name, agency):
    cl = Codelist(id=id, name=name, agency=agency)
    with pytest.raises(AttributeError):
        cl.description = "Description"


def test_iterable(id, name, agency):
    codes = [
        Code(id="child1", name="Child 1"),
        Code(id="child2", name="Child 2"),
    ]
    cl = Codelist(id=id, name=name, agency=agency, items=codes)

    assert isinstance(cl, Iterable)
    out = [c.id for c in cl]
    assert len(out) == 2
    assert out == ["child1", "child2"]


def test_sized(id, name, agency):
    cl = Codelist(id=id, name=name, agency=agency)

    assert isinstance(cl, Sized)


def test_get_code(id, name, agency):
    id1 = "child1"
    id2 = "child2"
    id3 = "child3"

    c1 = Code(id=id1, name="Child 1")
    c2 = Code(id=id2, name="Child 2")
    codes = [c1, c2]
    cl = Codelist(id=id, name=name, agency=agency, items=codes)

    resp1 = cl[id1]
    resp2 = cl[id3]

    assert resp1 == c1
    assert (id1 in cl) is True
    assert resp2 is None
    assert (id3 in cl) is False
