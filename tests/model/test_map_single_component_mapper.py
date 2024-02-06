import pytest

from pysdmx.model import ComponentMap, ValueMap


@pytest.fixture()
def source():
    return "COUNTRY"


@pytest.fixture()
def target():
    return "REF_AREA"


@pytest.fixture()
def values():
    vm1 = ValueMap("AR", "ARG")
    vm2 = ValueMap("UY", "URY")
    return [vm1, vm2]


def test_full_instantiation(source, target, values):
    m = ComponentMap(source, target, values)

    assert m.source == source
    assert m.target == target
    assert m.values == values


def test_immutable(source, target, values):
    m = ComponentMap(source, target, values)
    with pytest.raises(AttributeError):
        m.values = values


def test_equal(source, target, values):
    m1 = ComponentMap(source, target, values)
    m2 = ComponentMap(source, target, values)

    assert m1 == m2


def test_not_equal(source, target, values):
    m1 = ComponentMap(source, target, values)
    m2 = ComponentMap(source, source, [])

    assert m1 != m2
