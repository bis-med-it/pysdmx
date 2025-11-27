import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonDataStructuresMessage
from pysdmx.model import Component, Components, DataStructureDefinition


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/dsd/dsd_only.json", "rb"
    ) as f:
        return f.read()


@pytest.fixture
def body_two_cubes():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/dsd/dsd_two_cubes.json", "rb"
    ) as f:
        return f.read()


def test_dsd_only(body):
    res = msgspec.json.Decoder(JsonDataStructuresMessage).decode(body)
    dsds = res.to_model()

    assert len(dsds) == 1
    dsd = dsds[0]
    assert isinstance(dsd, DataStructureDefinition)
    assert dsd.agency == "BIS"
    assert dsd.id == "BIS_CBS"
    assert dsd.version == "1.42"
    assert isinstance(dsd.components, Components)
    assert len(dsd.components) == 24
    for comp in dsd.components:
        assert isinstance(comp, Component)
        assert comp.id is not None
        assert comp.name is None
        assert comp.concept is not None
        assert comp.concept.id is not None
        assert comp.id == comp.concept.item_id
        assert comp.required is not None
        assert comp.role is not None
        assert comp.dtype is not None


def test_dsd_two_cubes(body_two_cubes):
    res = msgspec.json.Decoder(JsonDataStructuresMessage).decode(
        body_two_cubes
    )
    dsds = res.to_model()

    assert len(dsds) == 1
    dsd = dsds[0]
    assert isinstance(dsd, DataStructureDefinition)
    assert dsd.agency == "BIS"
    assert dsd.id == "BIS_CBS"
    assert dsd.version == "1.0"
    assert len(dsd.components) == 24
    for comp in dsd.components:
        if comp.id == "CBS_BANK_TYPE":
            assert len(comp.enumeration) == 249
        elif comp.id == "CURR_TYPE_BOOK":
            assert len(comp.enumeration) == 4
