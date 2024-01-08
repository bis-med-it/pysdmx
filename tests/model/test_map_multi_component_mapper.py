import pytest

from pysdmx.model import MultiComponentMap, MultiValueMap


@pytest.fixture()
def source():
    return ["REF_AREA", "CURRENCY"]


@pytest.fixture()
def target():
    return "CURRENCY"


@pytest.fixture()
def values():
    vm1 = MultiValueMap(["CH", "LC1"], ["CHF"])
    vm2 = MultiValueMap(["CH", "CHF"], ["CHF"])
    vm3 = MultiValueMap(["DE", "LC1"], ["EUR"])
    return [vm1, vm2, vm3]


def test_full_instantiation(source, target, values):
    m = MultiComponentMap(source, target, values)

    assert m.source == source
    assert m.target == target
    assert m.values == values


def test_immutable(source, target, values):
    m = MultiComponentMap(source, target, values)
    with pytest.raises(AttributeError):
        m.values = values


def test_equal(source, target, values):
    m1 = MultiComponentMap(source, target, values)
    m2 = MultiComponentMap(source, target, values)

    assert m1 == m2


def test_not_equal(source, target, values):
    m1 = MultiComponentMap(source, target, values)
    m2 = MultiComponentMap(source, source, [])

    assert m1 != m2
