import pytest

import tests.api.fmr.code_map_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/", StructureFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2", StructureFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def query(fmr):
    res = "/structure/representationmap/"
    provider = "BIS"
    id = "ISO3166-A3_2_CTY"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{provider}/{id}/{version}/"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/map/code_map.json", "rb") as f:
        return f.read()


@pytest.fixture
def multi_query(fmr):
    res = "/structure/representationmap/"
    provider = "BIS"
    id = "CONSOLIDATE_ADDRESS_FIELDS"
    version = "1.42"
    return f"{fmr.api_endpoint}{res}{provider}/{id}/{version}/"


@pytest.fixture
def multi_body():
    with open("tests/api/fmr/samples/map/multi_code_map.json", "rb") as f:
        return f.read()


def test_returns_code_map(respx_mock, fmr, query, body):
    """get_code_map() should return a list of code mappings."""
    checks.check_code_mapping_core(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_mapping_details(respx_mock, async_fmr, query, body):
    """The response contains the expected mappings."""
    await checks.check_code_mapping_details(respx_mock, async_fmr, query, body)


def test_returns_multi_code_map(respx_mock, fmr, multi_query, multi_body):
    """get_code_map() should return a list of code mappings (multi)."""
    checks.check_multi_code_mapping_core(
        respx_mock, fmr, multi_query, multi_body
    )


@pytest.mark.asyncio
async def test_multi_mapping_details(
    respx_mock, async_fmr, multi_query, multi_body
):
    """The response contains the expected mappings (multi)."""
    await checks.check_multi_code_mapping_details(
        respx_mock, async_fmr, multi_query, multi_body
    )
