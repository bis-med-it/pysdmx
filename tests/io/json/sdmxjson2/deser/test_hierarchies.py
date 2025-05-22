import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonHierarchiesMessage
from pysdmx.model import Hierarchy


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/hier/hier.json", "rb"
    ) as f:
        return f.read()


def test_hierarchies_deser(body):
    res = msgspec.json.Decoder(JsonHierarchiesMessage).decode(body)
    hierarchies = res.to_model()

    assert len(hierarchies) == 2
    for h in hierarchies:
        assert isinstance(h, Hierarchy)
        assert h.version in ["1.0", "1.42"]
