from datetime import datetime, timezone
from typing import Iterable, Sized

import msgspec
import pytest

from pysdmx.model import decoders, encoders, RepresentationMap, ValueMap


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
    return "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL1(1.0)"


@pytest.fixture()
def target():
    return "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL2(1.0)"


@pytest.fixture()
def version():
    return "2.0"


@pytest.fixture()
def desc():
    return "my desc"


@pytest.fixture()
def mappings():
    vm1 = ValueMap(
        source="AR",
        target="ARG",
        valid_from=datetime(2000, 1, 1, tzinfo=timezone.utc),
        valid_to=datetime(2024, 1, 1, tzinfo=timezone.utc),
    )
    vm2 = ValueMap(source="UY", target="URY")
    return [vm1, vm2]


def test_default_initialization(id, name, agency, source, target, mappings):
    sm = RepresentationMap(
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
    sm = RepresentationMap(
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
    sm = RepresentationMap(
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
    sm = RepresentationMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
    )

    assert isinstance(sm, Iterable)

    for m in sm:
        assert isinstance(m, ValueMap)


def test_sized(id, name, agency, source, target, mappings):
    sm = RepresentationMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
    )

    assert isinstance(sm, Sized)
    assert len(sm) == len(mappings)


def test_serialization(
    id, name, agency, source, target, mappings, version, desc
):
    rm = RepresentationMap(
        id=id,
        name=name,
        agency=agency,
        source=source,
        target=target,
        maps=mappings,
        description=desc,
        version=version,
    )

    ser = msgspec.msgpack.Encoder(enc_hook=encoders).encode(rm)
    out = msgspec.msgpack.Decoder(RepresentationMap, dec_hook=decoders).decode(
        ser
    )
    assert out == rm
