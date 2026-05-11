import httpx
import pytest

from pysdmx.api.dc.rest import SdmxConnector
from pysdmx.errors import InternalError, NotFound
from pysdmx.model import Agency, Dataflow, DataflowRef


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
def json_availability():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/flows/flows.json", "rb"
    ) as f:
        return f.read()


@pytest.fixture
def csv_data():
    with open("tests/io/csv/sdmx20/reader/samples/data_v2.csv", "rb") as f:
        return f.read()


@pytest.fixture
def query_flows(host):
    return f"{host}/structure/dataflow?detail=allcompletestubs"


@pytest.fixture
def query_availability(host):
    return f"{host}/availability/dataflow/BIS/CBS/1.0?references=all"


@pytest.fixture
def query_data(host):
    return (
        f"{host}/data/dataflow/BIS/BIS_DER/1.0"
        "?dimensionAtObservation=AllDimensions"
    )


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


def test_search_dataflows_empty_query(
    respx_mock, rest_client, query_flows, json_flows
):
    respx_mock.get(query_flows).mock(
        return_value=httpx.Response(200, content=json_flows)
    )

    flows = rest_client.dataflows(" ")

    assert len(flows) == 5


def test_flows_nf(respx_mock, rest_client, query_flows):
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


def test_availability(
    respx_mock, rest_client, query_availability, json_availability
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    dfref = DataflowRef("BIS", "CBS", "1.0")

    flow = rest_client.dataflow(dfref)

    assert isinstance(flow, Dataflow)


def test_availability_dfstr(
    respx_mock, rest_client, query_availability, json_availability
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    dfref = "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:CBS(1.0)"

    flow = rest_client.dataflow(dfref)

    assert isinstance(flow, Dataflow)


def test_availability_agency(
    respx_mock, rest_client, query_availability, json_availability
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    dfref = Dataflow("CBS", agency=Agency("BIS"))

    flow = rest_client.dataflow(dfref)

    assert isinstance(flow, Dataflow)


def test_availability_nf(respx_mock, rest_client, query_availability):
    respx_mock.get(query_availability).mock(return_value=httpx.Response(404))
    dfref = "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:CBS(1.0)"

    with pytest.raises(NotFound):
        rest_client.dataflow(dfref)


def test_availability_deser_issues(
    respx_mock, rest_client, query_availability, unexpected_json
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=unexpected_json)
    )
    dfref = "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:CBS(1.0)"

    with pytest.raises(InternalError):
        rest_client.dataflow(dfref)


def test_data_query(respx_mock, rest_client, query_data, csv_data):
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = DataflowRef("BIS", "BIS_DER", "1.0")

    data = list(rest_client.data(dfref))

    assert len(data) == 20
    for row in data:
        assert isinstance(row, dict)


def test_data_query_dfstr(respx_mock, rest_client, query_data, csv_data):
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )
    dfref = (
        "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:BIS_DER(1.0)"
    )

    data = list(rest_client.data(dfref))

    assert len(data) == 20
    for row in data:
        assert isinstance(row, dict)


def test_data_nf(respx_mock, rest_client, query_data):
    respx_mock.get(query_data).mock(return_value=httpx.Response(404))
    dfref = (
        "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:BIS_DER(1.0)"
    )

    with pytest.raises(NotFound):
        for _ in rest_client.data(dfref):
            pass
