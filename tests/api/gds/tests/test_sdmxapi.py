import pytest

import tests.api.gds.checks.sdmxapi_checks as checks
from pysdmx.api.gds import GdsClient, GDS_BASE_ENDPOINT
from pysdmx.io.format import GdsFormat
from tests.api.gds import BASE_SAMPLES_PATH

ENDPOINT = "sdmxapi"
SAMPLES_PATH = BASE_SAMPLES_PATH / ENDPOINT
VALUE = "2.0.0"


@pytest.fixture
def gds() -> GdsClient:
    return GdsClient(
        GDS_BASE_ENDPOINT, GdsFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def query(gds: GdsClient) -> str:
    return f"{gds.api_endpoint}/{ENDPOINT}/{VALUE}"


@pytest.fixture
def body():
    with open(SAMPLES_PATH / f"{ENDPOINT}.json", "rb") as f:
        return f.read()


def test_returns_sdmx_api(respx_mock, gds, query, body):
    """get_sdmxapi() should return a collection of SDMX available APIs."""
    checks.check(respx_mock, gds, query, body, VALUE)
