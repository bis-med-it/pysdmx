import pytest

import tests.api.gds.checks.service_checks as checks
from pysdmx.api.gds import GdsClient, GDS_BASE_ENDPOINT
from pysdmx.api.qb.util import REST_ALL
from pysdmx.io.format import GdsFormat
from tests.api.gds import BASE_SAMPLES_PATH

ENDPOINT = "service"
SAMPLES_PATH = BASE_SAMPLES_PATH / ENDPOINT
VALUE = "BIS"
RESOURCE_ID = REST_ALL
VERSION = REST_ALL


@pytest.fixture
def gds() -> GdsClient:
    return GdsClient(
        GDS_BASE_ENDPOINT, GdsFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def query(gds: GdsClient) -> str:
    return f"{gds.api_endpoint}/{ENDPOINT}/{VALUE}/{RESOURCE_ID}/{VERSION}"


@pytest.fixture
def body():
    with open(SAMPLES_PATH / f"{ENDPOINT}.json", "rb") as f:
        return f.read()


def test_returns_services(respx_mock, gds, query, body):
    """get_agencies() should return a collection of organizations."""
    checks.check(respx_mock, gds, query, body, VALUE)
