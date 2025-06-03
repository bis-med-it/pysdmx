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
