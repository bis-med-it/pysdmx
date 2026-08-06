import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonRepresentationMapsMessage
from pysdmx.model import RepresentationMap


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/maps/code_maps_stubs.json", "rb"
    ) as f:
        return f.read()


def test_stub_ts_deser(body):
    res = msgspec.json.Decoder(JsonRepresentationMapsMessage).decode(body)

    rms = res.to_model()

    assert len(rms) == 1
    rm = rms[0]
    assert isinstance(rm, RepresentationMap)
    assert rm.agency == "BIS"
    assert rm.id == "AREA2ADJUST"
    assert rm.version == "1.0"
    assert rm.name == "REF_AREA to ADJUST_CODED"
    assert rm.description is None
    assert rm.is_external_reference is True
    assert rm.source is None
    assert rm.target is None
    assert len(rm.maps) == 0


