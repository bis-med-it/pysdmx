import pytest

from pysdmx.model import MultipleComponentMapper, MultipleValueMap


@pytest.fixture()
def source():
    return ["REF_AREA", "CURRENCY"]


@pytest.fixture()
def target():
    return "CURRENCY"


@pytest.fixture()
def values():
    vm1 = MultipleValueMap(["CH", "LC1"], ["CHF"])
    vm2 = MultipleValueMap(["CH", "CHF"], ["CHF"])
    vm3 = MultipleValueMap(["DE", "LC1"], ["EUR"])
    return [vm1, vm2, vm3]


def test_full_instantiation(source, target, values):
    m = MultipleComponentMapper(source, target, values)

    assert m.source == source
    assert m.target == target
    assert m.values == values


def test_immutable(source, target, values):
    m = MultipleComponentMapper(source, target, values)
    with pytest.raises(AttributeError):
        m.values = values


def test_equal(source, target, values):
    m1 = MultipleComponentMapper(source, target, values)
    m2 = MultipleComponentMapper(source, target, values)

    assert m1 == m2


def test_not_equal(source, target, values):
    m1 = MultipleComponentMapper(source, target, values)
    m2 = MultipleComponentMapper(source, source, [])

    assert m1 != m2
