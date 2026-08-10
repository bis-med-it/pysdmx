import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonTransfoMsg
from pysdmx.model import TransformationScheme


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/vtl/ts_stubs.json", "rb"
    ) as f:
        return f.read()


def test_stub_ts_deser(body):
    res = msgspec.json.Decoder(JsonTransfoMsg).decode(body)

    ts = res.to_model()

    assert isinstance(ts, TransformationScheme)
    assert ts.agency == "FR1"
    assert ts.id == "BPE_CENSUS"
    assert ts.version == "1.0"
    assert ts.name == "Transformation Scheme for BPE - CENSUS"
    assert ts.description is None
    assert ts.is_partial is False
    assert ts.is_external_reference is True
