import pytest

import tests.api.gds.checks.urn_checks as checks
from pysdmx.api.gds import GDS_BASE_ENDPOINT, GdsClient
from pysdmx.io.format import GdsFormat
from tests.api.gds import BASE_SAMPLES_PATH

ENDPOINT = "urn_resolver"
SAMPLES_PATH = BASE_SAMPLES_PATH / ENDPOINT
VALUE = ("urn:sdmx:org.sdmx.infomodel.categoryscheme."
         "CategoryScheme=BIS:BISWEB_CATSCHEME(1.0)")


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


def test_returns_urn_resolver(respx_mock, gds, query, body):
    """get_urn() should return the resolution of the URN."""
    checks.check(respx_mock, gds, query, body, VALUE)
