import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonConsumerMessage
from pysdmx.model import DataConsumer, DataConsumerScheme


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/consumer/dcs.json", "rb"
    ) as f:
        return f.read()


def test_dsd_only(body):
    res = msgspec.json.Decoder(JsonConsumerMessage).decode(body)
    dcs = res.to_model()

    assert len(dcs) == 1
    scheme = dcs[0]
    assert isinstance(scheme, DataConsumerScheme)
    assert scheme.agency == "BIS"
    assert scheme.id == "DATA_CONSUMERS"
    assert scheme.version == "1.0"
    assert len(scheme.consumers) == 1
    for consumer in scheme.consumers:
        assert isinstance(consumer, DataConsumer)
        assert consumer.id == "TEST_CONSUMER"
        assert consumer.name == "Test data consumer"
        assert consumer.description is None
        assert consumer.annotations == ()
        assert consumer.contacts == ()
        assert consumer.dataflows == ()
