import pytest

from pysdmx.model import FixedValueMap


@pytest.fixture()
def target():
    return "CONF_STATUS"


@pytest.fixture()
def value():
    return "C"


@pytest.fixture()
def located_in():
    return "source"


def test_default_instantiation(target, value):
    m = FixedValueMap(target, value)

    assert m.target == target
    assert m.value == value
    assert m.located_in == "target"


def test_full_instantiation(target, value, located_in):
    m = FixedValueMap(target, value, located_in)

    assert m.target == target
    assert m.value == value
    assert m.located_in == located_in


def test_immutable(target, value):
    m = FixedValueMap(target, value)
    with pytest.raises(AttributeError):
        m.located_in = "source"


def test_equal(target, value, located_in):
    m1 = FixedValueMap(target, value, located_in)
    m2 = FixedValueMap(target, value, located_in)

    assert m1 == m2


def test_not_equal(target, value, located_in):
    m1 = FixedValueMap(target, value, located_in)
    m2 = FixedValueMap(target, value + value, located_in)

    assert m1 != m2
