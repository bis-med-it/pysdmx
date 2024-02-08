from typing import Iterable, Sized

import pytest

from pysdmx.model import RepresentationMap, ValueMap


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
    vm1 = ValueMap("AR", "ARG")
    vm2 = ValueMap("UY", "URY")
    return [vm1, vm2]


def test_default_initialization(id, name, agency, source, target, mappings):
    sm = RepresentationMap(id, name, agency, source, target, mappings)

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
    sm = RepresentationMap(id, name, agency, source, target, mappings)

    with pytest.raises(AttributeError):
        sm.description = "blah"


def test_iterable(id, name, agency, source, target, mappings):
    sm = RepresentationMap(id, name, agency, source, target, mappings)

    assert isinstance(sm, Iterable)

    for m in sm:
        assert isinstance(m, ValueMap)


def test_sized(id, name, agency, source, target, mappings):
    sm = RepresentationMap(id, name, agency, source, target, mappings)

    assert isinstance(sm, Sized)
    assert len(sm) == len(mappings)
