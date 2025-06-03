import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonDataflowsMessage
from pysdmx.model import Dataflow, DataStructureDefinition


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows.json", "rb"
    ) as f:
        return f.read()


@pytest.fixture
def body_no_match():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows_no_match.json",
        "rb",
    ) as f:
        return f.read()


def test_dataflows_with_references(body):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert isinstance(flow.structure, DataStructureDefinition)


def test_dataflows_no_dsd_match(body_no_match):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body_no_match)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert isinstance(flow.structure, str)
