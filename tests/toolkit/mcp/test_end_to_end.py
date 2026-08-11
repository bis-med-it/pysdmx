"""End-to-end tests over mocked HTTP.

The other server tests inject a fake connector to exercise branches
deterministically. These ones go through the real ``PandasConnector``
against ``respx``-mocked responses, so that a change in how pysdmx
builds SDMX-REST URLs or parses SDMX-CSV is caught here rather than in
production.
"""

import httpx
import pytest

from pysdmx.toolkit.mcp import server


@pytest.fixture
def host():
    return "https://test.org"


@pytest.fixture
def json_availability():
    with open("tests/io/samples/bis_der.json", "rb") as f:
        return f.read()


@pytest.fixture
def csv_data():
    with open("tests/io/csv/sdmx20/reader/samples/data_v2.csv", "rb") as f:
        return f.read()


@pytest.fixture
def query_availability(host):
    return f"{host}/availability/dataflow/BIS/BIS_DER/1.0?references=all"


@pytest.fixture
def query_data(host):
    return (
        f"{host}/data/dataflow/BIS/BIS_DER/1.0"
        "?dimensionAtObservation=AllDimensions"
    )


def test_inspect_dataflow_over_http(
    respx_mock, host, query_availability, json_availability
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )

    result = server.inspect_dataflow("BIS:BIS_DER(1.0)", service=host)

    assert result.service == host
    assert result.ref == "BIS:BIS_DER(1.0)"
    assert result.dimensions
    assert result.availability_note
    assert result.next_step


def test_get_data_over_http_returns_observations(
    respx_mock,
    host,
    query_availability,
    query_data,
    json_availability,
    csv_data,
):
    respx_mock.get(query_availability).mock(
        return_value=httpx.Response(200, content=json_availability)
    )
    respx_mock.get(query_data).mock(
        return_value=httpx.Response(200, content=csv_data)
    )

    result = server.get_data("BIS:BIS_DER(1.0)", service=host)

    # The whole point of this server: numbers, not a query URL.
    assert result.row_count > 0
    assert result.records
    assert "OBS_VALUE" in result.columns
    assert result.truncated is False


def test_errors_are_classified_over_http(respx_mock, host):
    respx_mock.get(
        f"{host}/availability/dataflow/BIS/NOPE/1.0?references=all"
    ).mock(return_value=httpx.Response(404))

    with pytest.raises(Exception, match=r"\[not_found\]"):
        server.inspect_dataflow("BIS:NOPE(1.0)", service=host)


def test_server_errors_are_classified_over_http(respx_mock, host):
    respx_mock.get(
        f"{host}/availability/dataflow/BIS/BOOM/1.0?references=all"
    ).mock(return_value=httpx.Response(500))

    with pytest.raises(Exception, match=r"\[internal_error\]"):
        server.inspect_dataflow("BIS:BOOM(1.0)", service=host)
