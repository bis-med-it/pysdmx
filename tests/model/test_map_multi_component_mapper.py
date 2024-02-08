from typing import Iterable, Sized

import pytest

from pysdmx.model import (
    MultiComponentMap,
    MultiRepresentationMap,
    MultiValueMap,
)


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
    vms = [vm1, vm2, vm3]
    return MultiRepresentationMap(
        "RM_ID", "Map ISO2 to ISO3", "BIS", "SRC_CL", "TGT_CL", vms
    )


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
    m2 = MultiComponentMap(
        source,
        source,
        MultiRepresentationMap(
            "RM_ID1", "Map ISO2 to ISO3", "BIS", "SRC_CL1", "TGT_CL1", []
        ),
    )

    assert m1 != m2


def test_iterable(source, target, values):
    m = MultiComponentMap(source, target, values)

    assert isinstance(m.values, Iterable)

    for i in m.values:
        assert isinstance(i, MultiValueMap)


def test_sized(source, target, values):
    m = MultiComponentMap(source, target, values)

    assert isinstance(m.values, Sized)
    assert len(m.values) == 3
