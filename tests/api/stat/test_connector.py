from io import BytesIO
from pathlib import Path

import httpx
import pytest

from pysdmx.api.qb import ApiVersion, DataFormat, StructureFormat
from pysdmx.api.stat import StatConnector, StatEndpoints
from pysdmx.errors import InternalError, Invalid, NotFound, Unavailable
from pysdmx.io import get_datasets
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Schema

# --- Sample fixture files ----------------------------------------------------
_SAMPLES = Path(__file__).parent / "samples"
OECD_STRUCTURE = _SAMPLES / "oecd_g20_prices_structure.xml"
OECD_DATA = _SAMPLES / "oecd_g20_prices_data.csv"

# --- Reference dataflow ------------------------------------------------------
HOST = "https://test.stat"
OECD_FLOW = ("OECD.SDD.TPS", "DSD_G20_PRICES@DF_G20_PRICES", "1.0")
OECD_URN = "Dataflow=OECD.SDD.TPS:DSD_G20_PRICES@DF_G20_PRICES(1.0)"
OECD_KEY = "CHN.A.N.CPI.PA._T.N.GY"
# Matched by prefix (stops before the ``@`` in the dataflow id).
STRUCT_PREFIX = f"{HOST}/structure/dataflow/OECD.SDD.TPS"
DATA_PREFIX = f"{HOST}/data/dataflow/OECD.SDD.TPS"

# 404 -> NotFound, other 4xx -> Invalid, 5xx -> InternalError.
_ERROR_CASES = [
    (404, NotFound),
    (400, Invalid),
    (409, Invalid),
    (500, InternalError),
    (503, InternalError),
]


def _mock(respx_mock, url, content):
    """Mock an SDMX-REST GET (matched by URL prefix) with raw bytes."""
    return respx_mock.get(url__startswith=url).mock(
        return_value=httpx.Response(200, content=content)
    )


@pytest.fixture
def client():
    return StatConnector(HOST)


@pytest.fixture
def structure_bytes():
    return OECD_STRUCTURE.read_bytes()


@pytest.fixture
def data_bytes():
    return OECD_DATA.read_bytes()


# --- Construction / configuration --------------------------------------------
def test_init_defaults_to_oecd():
    conn = StatConnector()

    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


def test_init_configures_rest_service(client):
    svc = client._svc

    assert svc._api_endpoint == HOST
    assert svc._api_version == ApiVersion.V2_0_0
    assert svc._data_format == DataFormat.SDMX_CSV_1_0_0
    assert svc._structure_format == StructureFormat.SDMX_ML_2_1


def test_init_accepts_endpoint_enum():
    conn = StatConnector(StatEndpoints.OECD)

    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


def test_stat_endpoints_are_urls():
    assert len(StatEndpoints) >= 6
    for endpoint in StatEndpoints:
        assert endpoint.value.startswith(("http://", "https://"))
    # The verified group are SDMX-REST v2 bases.
    verified = {
        StatEndpoints.OECD,
        StatEndpoints.ILO,
        StatEndpoints.ABS,
        StatEndpoints.PACIFIC,
        StatEndpoints.STATEC,
        StatEndpoints.SIMEL_SV,
    }
    for endpoint in verified:
        assert endpoint.value.endswith("/rest/v2")


# --- fetch_structure ---------------------------------------------------------
def test_fetch_structure_returns_raw_bytes(
    respx_mock, client, structure_bytes
):
    route = _mock(respx_mock, STRUCT_PREFIX, structure_bytes)

    out = client.fetch_structure(*OECD_FLOW)

    assert out == structure_bytes
    assert route.called
    assert "/structure/dataflow/" in str(route.calls.last.request.url)


def test_fetch_structure_builds_url(respx_mock, client, structure_bytes):
    route = _mock(respx_mock, STRUCT_PREFIX, structure_bytes)

    client.fetch_structure(*OECD_FLOW)

    url = str(route.calls.last.request.url)
    assert "/structure/dataflow/OECD.SDD.TPS/" in url
    assert "DSD_G20_PRICES" in url
    assert "DF_G20_PRICES" in url
    assert "/1.0" in url
    assert "references=descendants" in url


def test_fetch_structure_accept_header(respx_mock, client, structure_bytes):
    route = _mock(respx_mock, STRUCT_PREFIX, structure_bytes)

    client.fetch_structure(*OECD_FLOW)

    assert (
        route.calls.last.request.headers["Accept"]
        == "application/vnd.sdmx.structure+xml;version=2.1"
    )


# --- fetch_data --------------------------------------------------------------
def test_fetch_data_returns_raw_bytes(respx_mock, client, data_bytes):
    route = _mock(respx_mock, DATA_PREFIX, data_bytes)

    out = client.fetch_data(*OECD_FLOW)

    assert out == data_bytes
    url = str(route.calls.last.request.url)
    # The default key ("*") is omitted from the path.
    assert url.endswith("dimensionAtObservation=AllDimensions")
    assert "/1.0/" not in url


def test_fetch_data_with_key_in_url(respx_mock, client, data_bytes):
    route = _mock(respx_mock, DATA_PREFIX, data_bytes)

    out = client.fetch_data(*OECD_FLOW, key=OECD_KEY)

    assert out == data_bytes
    url = str(route.calls.last.request.url)
    assert f"/1.0/{OECD_KEY}" in url
    assert "dimensionAtObservation=AllDimensions" in url


def test_fetch_data_accept_header(respx_mock, client, data_bytes):
    route = _mock(respx_mock, DATA_PREFIX, data_bytes)

    client.fetch_data(*OECD_FLOW)

    assert (
        route.calls.last.request.headers["Accept"]
        == "application/vnd.sdmx.data+csv;version=1.0.0"
    )


# --- fetch_dataset -----------------------------------------------------------
def test_fetch_dataset_returns_pandas_dataset(
    respx_mock, client, structure_bytes, data_bytes
):
    _mock(respx_mock, STRUCT_PREFIX, structure_bytes)
    _mock(respx_mock, DATA_PREFIX, data_bytes)
    expected = get_datasets(
        BytesIO(data_bytes), BytesIO(structure_bytes), validate=False
    )[0]

    ds = client.fetch_dataset(*OECD_FLOW)

    assert isinstance(ds, PandasDataset)
    assert isinstance(ds.structure, Schema)
    assert ds.structure.short_urn == OECD_URN
    assert ds.data.equals(expected.data)


def test_fetch_dataset_passes_key_to_data(
    respx_mock, client, structure_bytes, data_bytes
):
    _mock(respx_mock, STRUCT_PREFIX, structure_bytes)
    data_route = _mock(respx_mock, DATA_PREFIX, data_bytes)

    client.fetch_dataset(*OECD_FLOW, key=OECD_KEY)

    assert f"/1.0/{OECD_KEY}" in str(data_route.calls.last.request.url)


# --- Error mapping -----------------------------------------------------------
@pytest.mark.parametrize(("status", "error"), _ERROR_CASES)
def test_fetch_structure_error_mapping(respx_mock, client, status, error):
    respx_mock.get(url__startswith=STRUCT_PREFIX).mock(
        return_value=httpx.Response(status, text="boom")
    )

    with pytest.raises(error):
        client.fetch_structure(*OECD_FLOW)


@pytest.mark.parametrize(("status", "error"), _ERROR_CASES)
def test_fetch_data_error_mapping(respx_mock, client, status, error):
    respx_mock.get(url__startswith=DATA_PREFIX).mock(
        return_value=httpx.Response(status, text="boom")
    )

    with pytest.raises(error):
        client.fetch_data(*OECD_FLOW)


def test_fetch_structure_connection_error(respx_mock, client):
    respx_mock.get(url__startswith=STRUCT_PREFIX).mock(
        side_effect=httpx.ConnectError("boom")
    )

    with pytest.raises(Unavailable):
        client.fetch_structure(*OECD_FLOW)


def test_fetch_data_connection_error(respx_mock, client):
    respx_mock.get(url__startswith=DATA_PREFIX).mock(
        side_effect=httpx.ConnectError("boom")
    )

    with pytest.raises(Unavailable):
        client.fetch_data(*OECD_FLOW)
