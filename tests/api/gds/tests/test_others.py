import pytest

from pysdmx.api.qb.gds import GdsQuery, GdsType
from pysdmx.api.qb.util import REST_ALL, REST_LATEST
from tests.api.gds.checks import agency_checks, service_checks
from msgspec import DecodeError
from pysdmx.api.gds import GdsClient, GDS_BASE_ENDPOINT
from pysdmx.api.qb import ApiVersion, StructureType
from pysdmx.errors import NotImplemented, Invalid
from pysdmx.io.format import GdsFormat, StructureFormat
from tests.api.gds import BASE_SAMPLES_PATH

AGENCY_ENDPOINT = "agency"
AGENCY_SAMPLES_PATH = BASE_SAMPLES_PATH / AGENCY_ENDPOINT
SERVICE_ENDPOINT = "service"
SERVICE_SAMPLES_PATH = BASE_SAMPLES_PATH / SERVICE_ENDPOINT
VALUE = "BIS"
RESOURCE = REST_ALL
VERSION = REST_LATEST
NON_EXISTING_AGENCY = "non_existing_agency"


@pytest.fixture
def gds_without_slash() -> GdsClient:
    return GdsClient(
        str(GDS_BASE_ENDPOINT)[:-1], GdsFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def gds_1_4_0() -> GdsClient:
    return GdsClient(
        str(GDS_BASE_ENDPOINT), GdsFormat.SDMX_JSON_2_0_0, ApiVersion.V1_4_0
    )


@pytest.fixture
def query(gds_without_slash: GdsClient) -> str:
    return f"{gds_without_slash.api_endpoint}/{AGENCY_ENDPOINT}/{VALUE}"


@pytest.fixture
def non_ext_agc_query(gds_without_slash: GdsClient) -> str:
    return f"{gds_without_slash.api_endpoint}/{AGENCY_ENDPOINT}/{NON_EXISTING_AGENCY}"


@pytest.fixture
def service_query(gds_without_slash: GdsClient) -> str:
    return f"{gds_without_slash.api_endpoint}/{SERVICE_ENDPOINT}/{VALUE}"


@pytest.fixture
def body():
    with open(AGENCY_SAMPLES_PATH / f"{AGENCY_ENDPOINT}.json", "rb") as f:
        return f.read()


@pytest.fixture
def invalid_body():
    with open(AGENCY_SAMPLES_PATH / f"{NON_EXISTING_AGENCY}.json", "rb") as f:
        return f.read()


@pytest.fixture
def service_body():
    with open(SERVICE_SAMPLES_PATH / f"{SERVICE_ENDPOINT}.json", "rb") as f:
        return f.read()


def test_query_with_slash(respx_mock, gds_without_slash, query, body):
    agency_checks.check(respx_mock, gds_without_slash, query, body, VALUE)


def test_non_existing_agency(respx_mock, gds_without_slash, non_ext_agc_query, invalid_body):
    with pytest.raises(DecodeError):
        agency_checks.check(respx_mock, gds_without_slash, non_ext_agc_query, invalid_body, NON_EXISTING_AGENCY)


def test_downgraded_version(respx_mock, gds_1_4_0, service_query, service_body):
    service_checks.check(respx_mock, gds_1_4_0, service_query, service_body, VALUE, version=VERSION)


def test_invalid_query():
    query = GdsQuery(artefact_type=StructureType.AGENCY_SCHEME)
    with pytest.raises(Invalid):
        query._get_base_url(version=VERSION)


def test_invalid_artefact_type():
    query = GdsQuery(artefact_type=GdsType.GDS_AGENCY)
    with pytest.raises(Invalid):
        query._GdsQuery__check_artefact_type(atyp=StructureType.AGENCY_SCHEME, version=ApiVersion.V2_0_0)


def test_invalid_gds_format():
    invalid_format = StructureFormat.SDMX_JSON_2_0_0
    with pytest.raises(NotImplemented, match="Unsupported format: only application/json are supported"):
        GdsClient(GDS_BASE_ENDPOINT, invalid_format)
