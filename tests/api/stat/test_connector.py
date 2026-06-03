import pytest

from pysdmx.api.qb import ApiVersion, DataFormat, StructureFormat
from pysdmx.api.stat import StatConnector, StatEndpoints


@pytest.fixture
def host():
    return "https://test.stat"


@pytest.fixture
def client(host):
    return StatConnector(host)


def test_init_defaults_to_oecd():
    conn = StatConnector()
    assert conn._svc._api_endpoint == StatEndpoints.OECD.value


def test_init_configures_rest_service(client):
    svc = client._svc
    assert svc._api_endpoint == "https://test.stat"
    assert svc._api_version == ApiVersion.V2_0_0
    assert svc._data_format == DataFormat.SDMX_CSV_1_0_0
    assert svc._structure_format == StructureFormat.SDMX_ML_2_1


def test_init_accepts_endpoint_enum():
    conn = StatConnector(StatEndpoints.OECD)
    assert conn._svc._api_endpoint == StatEndpoints.OECD.value
