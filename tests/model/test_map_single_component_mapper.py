from typing import Iterable, Sized

import pytest

from pysdmx.model import ComponentMap, RepresentationMap, ValueMap


@pytest.fixture()
def source():
    return "COUNTRY"


@pytest.fixture()
def target():
    return "REF_AREA"


@pytest.fixture()
def values():
    vm1 = ValueMap(source="AR", target="ARG")
    vm2 = ValueMap(source="UY", target="URY")
    vms = [vm1, vm2]
    return RepresentationMap(
        id="RM_ID",
        name="Map ISO2 to ISO3",
        agency="BIS",
        source="SRC_CL",
        target="TGT_CL",
        maps=vms,
    )


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
    m2 = ComponentMap(
        source,
        source,
        RepresentationMap(
            id="RM_ID2",
            name="Map ISO2 to ISO3",
            agency="BIS",
            source="SRC_CL1",
            target="TGT_CL1",
            maps=[],
        ),
    )

    assert m1 != m2


def test_iterable(source, target, values):
    m = ComponentMap(source, target, values)

    assert isinstance(m.values, Iterable)

    for i in m.values:
        assert isinstance(i, ValueMap)


def test_sized(source, target, values):
    m = ComponentMap(source, target, values)

    assert isinstance(m.values, Sized)
    assert len(m.values) == 2
