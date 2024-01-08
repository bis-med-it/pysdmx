from typing import Iterable, Sized
import uuid

import pytest

from pysdmx.model import (
    ComponentMap,
    DatePatternMap,
    FixedValueMap,
    ImplicitComponentMap,
    StructureMap,
    ValueMap,
)


@pytest.fixture()
def id():
    return "id"


@pytest.fixture()
def name():
    return "name"


@pytest.fixture()
def agency():
    return "5B0"


@pytest.fixture()
def source():
    return "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:CIBL(1.0)"


@pytest.fixture()
def target():
    return "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:CBS(1.0)"


@pytest.fixture()
def version():
    return "2.0"


@pytest.fixture()
def desc():
    return "my desc"


@pytest.fixture()
def mappings():
    m1 = ImplicitComponentMap("OBS_CONF", "CONF_STATUS")
    m2 = ImplicitComponentMap("OBS_STATUS", "OBS_STATUS")
    m3 = FixedValueMap("FREQ", "M")
    m4 = DatePatternMap("ACTIVITY_DATE", "TIME_PERIOD", "%B %Y", "M")
    m5 = ComponentMap("SRC1", "TGT1", [ValueMap("1", "A")])
    m6 = ComponentMap("SRC2", "TGT2", [ValueMap("2", "B")])
    m7 = ComponentMap("SRC3", "TGT3", [ValueMap("3", "C")])
    return [m1, m2, m3, m4, m5, m6, m7]


def test_default_initialization(id, name, agency, source, target, mappings):
    sm = StructureMap(id, name, agency, source, target, mappings)

    assert sm.id == id
    assert sm.name == name
    assert sm.agency == agency
    assert sm.source == source
    assert sm.target == target
    assert sm.maps == mappings
    assert sm.description is None
    assert sm.version == "1.0"


def test_full_initialization(
    id, name, agency, source, target, mappings, version, desc
):
    sm = StructureMap(
        id, name, agency, source, target, mappings, desc, version
    )

    assert sm.id == id
    assert sm.name == name
    assert sm.agency == agency
    assert sm.source == source
    assert sm.target == target
    assert sm.maps == mappings
    assert sm.description == desc
    assert sm.version == version


def test_immutable(id, name, agency, source, target, mappings):
    sm = StructureMap(id, name, agency, source, target, mappings)

    with pytest.raises(AttributeError):
        sm.description = "blah"


def test_iterable(id, name, agency, source, target, mappings):
    sm = StructureMap(id, name, agency, source, target, mappings)

    assert isinstance(sm, Iterable)

    for m in sm:
        assert (
            isinstance(m, ComponentMap)
            or isinstance(m, DatePatternMap)
            or isinstance(m, FixedValueMap)
            or isinstance(m, ImplicitComponentMap)
        )


def test_sized(id, name, agency, source, target, mappings):
    sm = StructureMap(id, name, agency, source, target, mappings)

    assert isinstance(sm, Sized)
    assert len(sm) == len(mappings)


def test_get_map(id, name, agency, source, target, mappings):
    sm = StructureMap(id, name, agency, source, target, mappings)

    id = mappings[3].source
    resp1 = sm[id]
    resp2 = sm[str(uuid.uuid4())]

    assert len(resp1) == 1
    assert resp1[0] == mappings[3]
    assert resp2 is None
