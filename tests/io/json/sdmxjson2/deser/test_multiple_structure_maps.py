import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonStructureMapsMessage
from pysdmx.model import StructureMap


@pytest.fixture
def body():
    with open("tests/io/json/sdmxjson2/deser/samples/maps/sm.json", "rb") as f:
        return f.read()


def test_multiple_structure_maps(body):
    res = msgspec.json.Decoder(JsonStructureMapsMessage).decode(body)
    maps = res.to_model()

    assert len(maps) == 2
    for m in maps:
        assert isinstance(m, StructureMap)
        assert m.version in ["1.0", "1.1"]


def test_representation_map_urn(body):
    res = msgspec.json.Decoder(JsonStructureMapsMessage).decode(body)
    maps = res.to_model()
    exp = "urn:sdmx:org.sdmx.infomodel.structuremapping.RepresentationMap"

    assert len(maps) == 2
    for m in maps:
        for cm in m.component_maps:
            assert isinstance(cm.values, str)
            assert cm.values.startswith(exp)
