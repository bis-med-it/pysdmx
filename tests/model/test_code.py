from datetime import datetime, timezone

import pytest

from pysdmx.model import Code


@pytest.fixture()
def id():
    return "UY"


@pytest.fixture()
def name():
    return "Uruguay"


@pytest.fixture()
def desc():
    return "The Oriental Republic of Uruguay"


@pytest.fixture()
def vf():
    return datetime(1828, 8, 27, 0, 0, 0, tzinfo=timezone.utc)


@pytest.fixture()
def vt():
    return None


def test_default(id):
    c = Code(id=id)

    assert c.id == id
    assert c.name is None
    assert c.description is None
    assert c.valid_from is None
    assert c.valid_to is None


def test_full_instantiation(id, name, desc, vf, vt):
    c = Code(id=id, name=name, description=desc, valid_from=vf, valid_to=vt)

    assert c.id == id
    assert c.name == name
    assert c.description == desc
    assert c.valid_from == vf
    assert c.valid_to == vt


def test_immutable(id, name):
    c = Code(id=id)
    with pytest.raises(AttributeError):
        c.name = name


def test_equal(id, name, desc):
    c1 = Code(id=id, name=name, description=desc)
    c2 = Code(id=id, name=name, description=desc)

    assert c1 == c2


def test_not_equal(id):
    c1 = Code(id=id)
    c2 = Code(id=id + id)

    assert c1 != c2


def test_tostr_id(id):
    c = Code(id=id)

    s = str(c)

    assert s == f"id={id}"


def test_tostr_name(id, name):
    c = Code(id=id, name=name)

    s = str(c)

    assert s == f"id={id}, name={name}"
