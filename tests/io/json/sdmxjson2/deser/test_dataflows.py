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


@pytest.fixture
def body_stubs():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows_stubs.json",
        "rb",
    ) as f:
        return f.read()


@pytest.fixture
def body_all_stubs():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows_all_stubs.json",
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
    assert flow.components == flow.structure.components
    assert flow.series_count == 42
    assert flow.obs_count == 42000


def test_dataflows_no_dsd_match(body_no_match):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body_no_match)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert isinstance(flow.structure, str)


def test_dataflows_stubs(body_stubs):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body_stubs)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert flow.structure is None


def test_dataflows_all_stubs(body_all_stubs):
    res = msgspec.json.Decoder(JsonDataflowsMessage).decode(body_all_stubs)
    flows = res.to_model()

    assert len(flows) == 1
    flow = flows[0]
    assert isinstance(flow, Dataflow)
    assert flow.structure is None
