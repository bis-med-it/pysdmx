from typing import Iterable, Sized
import uuid

import msgspec
import pytest

from pysdmx.model import (
    ComponentMap,
    DatePatternMap,
    decoders,
    encoders,
    FixedValueMap,
    ImplicitComponentMap,
    RepresentationMap,
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
    m4 = DatePatternMap("ACTIVITY_DATE", "TIME_PERIOD", "MMM YYYY", "M")
    m5 = ComponentMap(
        "SRC1",
        "TGT1",
        RepresentationMap(
            id="M1",
            name="M1",
            agency="BIS",
            source="CL1",
            target="CL2",
            maps=[ValueMap(source="1", target="A")],
        ),
    )
    m6 = ComponentMap(
        "SRC2",
        "TGT2",
        RepresentationMap(
            id="M1",
            name="M1",
            agency="BIS",
            source="CL1",
            target="CL2",
            maps=[ValueMap(source="2", target="B")],
        ),
    )
    m7 = ComponentMap(
        "SRC3",
        "TGT3",
        RepresentationMap(
            id="M1",
            name="M1",
            agency="BIS",
            source="CL1",
            target="CL2",
            maps=[ValueMap(source="3", target="C")],
        ),
    )
    return [m1, m2, m3, m4, m5, m6, m7]


def test_default_initialization(id, name, agency, source, target, mappings):
    sm = StructureMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
    )

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
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
        description=desc,
        version=version,
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
    sm = StructureMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
    )

    with pytest.raises(AttributeError):
        sm.description = "blah"


def test_iterable(id, name, agency, source, target, mappings):
    sm = StructureMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
    )

    assert isinstance(sm, Iterable)

    for m in sm:
        assert isinstance(
            m,
            (
                ComponentMap,
                DatePatternMap,
                FixedValueMap,
                ImplicitComponentMap,
            ),
        )


def test_sized(id, name, agency, source, target, mappings):
    sm = StructureMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
    )

    assert isinstance(sm, Sized)
    assert len(sm) == len(mappings)


def test_get_map(id, name, agency, source, target, mappings):
    sm = StructureMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
    )

    id = mappings[3].source
    resp1 = sm[id]
    resp2 = sm[str(uuid.uuid4())]

    assert len(resp1) == 1
    assert resp1[0] == mappings[3]
    assert resp2 is None


def test_serialization(
    id, name, agency, source, target, mappings, version, desc
):
    sm = StructureMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
        description=desc,
        version=version,
    )
    ser = msgspec.msgpack.Encoder(enc_hook=encoders).encode(sm)
    out = msgspec.msgpack.Decoder(StructureMap, dec_hook=decoders).decode(ser)
    assert out == sm
