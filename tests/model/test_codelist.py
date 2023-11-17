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


def test_defaults(id, name, agency):
    cl = Codelist(id, name, agency)

    assert cl.id == id
    assert cl.name == name
    assert cl.agency == agency
    assert cl.description is None
    assert cl.version == "1.0"
    assert cl.codes is not None
    assert len(cl.codes) == 0


def test_full_initialization(id, name, agency):
    desc = "description"
    version = "1.42.0"
    codes = [Code("child1", "Child 1"), Code("child2", "Child 2")]

    cl = Codelist(id, name, agency, desc, version, codes)

    assert cl.id == id
    assert cl.name == name
    assert cl.agency == agency
    assert cl.description == desc
    assert cl.version == version
    assert cl.codes == codes
    assert len(cl) == 2
    assert len(cl) == len(cl.codes)


def test_immutable(id, name, agency):
    cl = Codelist(id, name, agency)
    with pytest.raises(AttributeError):
        cl.description = "Description"


def test_iterable(id, name, agency):
    codes = [Code("child1", "Child 1"), Code("child2", "Child 2")]
    cl = Codelist(id, name, agency, codes=codes)

    assert isinstance(cl, Iterable)
    out = [c.id for c in cl]
    assert len(out) == 2
    assert out == ["child1", "child2"]


def test_sized(id, name, agency):
    cl = Codelist(id, name, agency)

    assert isinstance(cl, Sized)


def test_get_code(id, name, agency):
    c1 = Code("child1", "Child 1")
    c2 = Code("child2", "Child 2")
    codes = [c1, c2]
    cl = Codelist(id, name, agency, codes=codes)

    resp1 = cl["child1"]
    resp2 = cl["child3"]

    assert resp1 == c1
    assert resp2 is None
