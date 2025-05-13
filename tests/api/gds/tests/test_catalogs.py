import pytest

import tests.api.gds.checks.catalog_checks as checks
from pysdmx.api.gds import GdsClient, GDS_BASE_ENDPOINT
from pysdmx.api.qb.util import REST_ALL
from pysdmx.io.format import GdsFormat
from tests.api.gds import BASE_SAMPLES_PATH

ENDPOINT = "catalog"
SAMPLES_PATH = BASE_SAMPLES_PATH / ENDPOINT
VALUE = "BIS"
RESOURCE_ID = REST_ALL
VERSION = REST_ALL

params = {
    "resource_type": "data",
    "message_format": "json",
    "api_version": "2.0.0",
    "detail": "full",
    "references": "none",
}


@pytest.fixture
def gds() -> GdsClient:
    return GdsClient(
        GDS_BASE_ENDPOINT, GdsFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def query(gds: GdsClient) -> str:
    base_query = f"{gds.api_endpoint}/{ENDPOINT}/{VALUE}/{RESOURCE_ID}/{VERSION}/?"
    query_params = "&".join(f"{key}={value}" for key, value in params.items())
    return f"{base_query}{query_params}"

@pytest.fixture
def body():
    with open(SAMPLES_PATH / f"{ENDPOINT}.json", "rb") as f:
        return f.read()


def test_returns_catalogs(respx_mock, gds, query, body):
    """get_agencies() should return a collection of organizations."""
    checks.check(respx_mock, gds, query, body, VALUE, params)
