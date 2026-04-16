import httpx
import pytest

from pysdmx.api.dc.rest import SdmxConnector
from pysdmx.errors import InternalError, NotFound
from pysdmx.model import Dataflow


@pytest.fixture
def host():
    return "https://test.org"


@pytest.fixture
def rest_client(host):
    return SdmxConnector(host)


@pytest.fixture
def json_flows():
    with open("tests/api/fmr/samples/df/flows.json", "rb") as f:
        return f.read()


@pytest.fixture
def unexpected_json():
    with open("tests/api/fmr/samples/orgs/agencies.json", "rb") as f:
        return f.read()


@pytest.fixture
def query_flows(host):
    return f"{host}/structure/dataflow?detail=allcompletestubs"


def test_list_dataflows(respx_mock, rest_client, query_flows, json_flows):
    respx_mock.get(query_flows).mock(
        return_value=httpx.Response(200, content=json_flows)
    )

    flows = rest_client.dataflows()

    assert len(flows) == 5
    for f in flows:
        assert isinstance(f, Dataflow)


def test_search_dataflows(respx_mock, rest_client, query_flows, json_flows):
    respx_mock.get(query_flows).mock(
        return_value=httpx.Response(200, content=json_flows)
    )

    flows = rest_client.dataflows("facet")

    assert len(flows) == 1
    for f in flows:
        assert isinstance(f, Dataflow)
        assert f.id == "TEST_FACETS_FLOW"


def test_search_dataflows_empty(
    respx_mock, rest_client, query_flows, json_flows
):
    respx_mock.get(query_flows).mock(
        return_value=httpx.Response(200, content=json_flows)
    )

    flows = rest_client.dataflows(" ")

    assert len(flows) == 5


def test_list_no_flows(respx_mock, rest_client, query_flows):
    respx_mock.get(query_flows).mock(return_value=httpx.Response(404))

    with pytest.raises(NotFound):
        rest_client.dataflows()


def test_flows_deser_issue(
    respx_mock, rest_client, query_flows, unexpected_json
):
    respx_mock.get(query_flows).mock(
        return_value=httpx.Response(200, content=unexpected_json)
    )

    with pytest.raises(InternalError):
        rest_client.dataflows()
