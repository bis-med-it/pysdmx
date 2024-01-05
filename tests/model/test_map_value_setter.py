import pytest

from pysdmx.model import FixedValueMap


@pytest.fixture()
def target():
    return "CONF_STATUS"


@pytest.fixture()
def value():
    return "C"


def test_default_instantiation(target, value):
    m = FixedValueMap(target, value)

    assert m.target == target
    assert m.value == value
    assert m.is_fixed is True


def test_full_instantiation(target, value):
    m = FixedValueMap(target, value, False)

    assert m.target == target
    assert m.value == value
    assert m.is_fixed is False


def test_immutable(target, value):
    m = FixedValueMap(target, value)
    with pytest.raises(AttributeError):
        m.is_fixed = False


def test_equal(target, value):
    m1 = FixedValueMap(target, value)
    m2 = FixedValueMap(target, value)

    assert m1 == m2


def test_not_equal(target, value):
    m1 = FixedValueMap(target, value)
    m2 = FixedValueMap(target, value, False)

    assert m1 != m2
