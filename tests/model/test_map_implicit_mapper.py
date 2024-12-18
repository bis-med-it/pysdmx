import pytest

from pysdmx.model import ImplicitComponentMap


@pytest.fixture
def source():
    return "OBS_CONF"


@pytest.fixture
def target():
    return "CONF_STATUS"


def test_full_instantiation(source, target):
    m = ImplicitComponentMap(source, target)

    assert m.source == source
    assert m.target == target


def test_immutable(source, target):
    m = ImplicitComponentMap(source, target)
    with pytest.raises(AttributeError):
        m.target = source


def test_equal(source, target):
    m1 = ImplicitComponentMap(source, target)
    m2 = ImplicitComponentMap(source, target)

    assert m1 == m2


def test_not_equal(source, target):
    m1 = ImplicitComponentMap(source, target)
    m2 = ImplicitComponentMap(source, source)

    assert m1 != m2
