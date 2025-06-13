from typing import Iterable

import pytest

from pysdmx.model import MetadataAttribute


@pytest.fixture
def id():
    return "FX"


@pytest.fixture
def value():
    return 42


@pytest.fixture
def child():
    return MetadataAttribute("child", 422)


def test_default(id):
    attr = MetadataAttribute(id)

    assert attr.id == id
    assert attr.value is None
    assert len(attr.attributes) == 0


def test_full_instantiation(id, value, child):
    attr = MetadataAttribute(id, value, [child])

    assert attr.id == id
    assert attr.value == value
    assert len(attr.attributes) == 1


def test_immutable(id, value, child):
    attr = MetadataAttribute(id, value)
    with pytest.raises(AttributeError):
        attr.attributes = [child]


def test_equal(id, value):
    attr1 = MetadataAttribute(id, value)
    attr2 = MetadataAttribute(id, value)

    assert attr1 == attr2


def test_not_equal(id, value):
    attr1 = MetadataAttribute(id, value)
    attr2 = MetadataAttribute(id + id, value)

    assert attr1 != attr2


def test_iterable(id, value, child):
    children = [child]
    attr = MetadataAttribute(id, value, children)

    assert isinstance(attr, Iterable)
    out = [a.id for a in attr]
    assert len(out) == 1
    assert out == [child.id]


def test_tostr(id, value, child):
    children = [child]
    attr = MetadataAttribute(id, value, children)

    s = str(attr)

    assert s == f"id: {id}, value: {value}, attributes: 1 metadataattributes"


def test_tostr_empty():
    attr = MetadataAttribute("empty", attributes=[])

    s = str(attr)

    assert s == "id: empty"


def test_repr(id, value):
    attr = MetadataAttribute(id, value, attributes=[])

    r = repr(attr)

    assert r == f"MetadataAttribute(id={repr(id)}, value={repr(value)})"
