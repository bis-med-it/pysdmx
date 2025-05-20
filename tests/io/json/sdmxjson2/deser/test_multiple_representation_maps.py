import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonRepresentationMapsMessage
from pysdmx.model import RepresentationMap


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/maps/code_maps.json", "rb"
    ) as f:
        return f.read()


def test_annotation_with_uri(body):
    res = msgspec.json.Decoder(JsonRepresentationMapsMessage).decode(body)
    maps = res.to_model()

    assert len(maps) == 2
    for m in maps:
        assert isinstance(m, RepresentationMap)
        assert m.version in ["1.0", "1.1"]
