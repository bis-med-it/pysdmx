import pytest

from pysdmx.model import ValueSetter


@pytest.fixture()
def target():
    return "CONF_STATUS"


@pytest.fixture()
def value():
    return "C"


def test_default_instantiation(target, value):
    m = ValueSetter(target, value)

    assert m.target == target
    assert m.value == value
    assert m.is_fixed is True


def test_full_instantiation(target, value):
    m = ValueSetter(target, value, False)

    assert m.target == target
    assert m.value == value
    assert m.is_fixed is False


def test_immutable(target, value):
    m = ValueSetter(target, value)
    with pytest.raises(AttributeError):
        m.is_fixed = False


def test_equal(target, value):
    m1 = ValueSetter(target, value)
    m2 = ValueSetter(target, value)

    assert m1 == m2


def test_not_equal(target, value):
    m1 = ValueSetter(target, value)
    m2 = ValueSetter(target, value, False)

    assert m1 != m2
