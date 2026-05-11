import httpx
import pytest

from pysdmx.api.dc.query import Operator, TextFilter
from pysdmx.api.qb.data import DataContext, DataQuery
from pysdmx.api.qb.service import RestService
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def version() -> ApiVersion:
    return ApiVersion.V2_0_0


@pytest.fixture
def end_point() -> str:
    return "https://registry.sdmx.org/sdmx/v2"


@pytest.fixture
def service(end_point: str, version: ApiVersion) -> RestService:
    return RestService(end_point, version)


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/orgs/agencies.fusion.json", "rb") as f:
        return f.read()


def test_sanitize_asterisk(respx_mock, service: RestService, end_point, body):
    query = DataQuery(DataContext.DATAFLOW, "BIS", "EXR", "*", "M.USD.CHF")
    url = f"{end_point}/data/dataflow/BIS/EXR/%2A/M.USD.CHF/"
    route = respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=body)
    )

    service.data(query)

    assert route.called


def test_sanitize_comma(respx_mock, service: RestService, end_point, body):
    query = DataQuery(DataContext.DATAFLOW, "BIS", "EXR", "1.0,2.0")
    url = f"{end_point}/data/dataflow/BIS/EXR/1.0%2C2.0/"
    route = respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=body)
    )

    service.data(query)

    assert route.called


def test_sanitize_plus_sign(respx_mock, service: RestService, end_point, body):
    query = DataQuery(DataContext.DATAFLOW, "BIS", "EXR", "+")
    url = f"{end_point}/data/dataflow/BIS/EXR/%2B/"
    route = respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=body)
    )

    service.data(query)

    assert route.called


def test_sanitize_square_brackets(
    respx_mock, service: RestService, end_point, body
):
    flt = TextFilter("CUR", Operator.EQUALS, "CHF")
    query = DataQuery(DataContext.DATAFLOW, "BIS", "EXR", components=flt)
    url = f"{end_point}/data/dataflow/BIS/EXR?c%5BCUR%5D=CHF"
    route = respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=body)
    )

    service.data(query)

    assert route.called


def test_sanitize_colon(respx_mock, service: RestService, end_point, body):
    flt = TextFilter(
        "TIME_PERIOD", Operator.GREATER_THAN_OR_EQUAL, "2026-01-01"
    )
    query = DataQuery(DataContext.DATAFLOW, "BIS", "EXR", components=flt)
    url = (
        f"{end_point}/data/dataflow/BIS/EXR?c%5BTIME_PERIOD%5D=ge%3A2026-01-01"
    )
    route = respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=body)
    )

    service.data(query)

    assert route.called
