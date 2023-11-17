import pytest
import tests.fmr.code_map_checks as checks

from pysdmx.fmr import AsyncRegistryClient, Format, RegistryClient


@pytest.fixture()
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def query(fmr):
    res = "structure/representationmap/"
    provider = "BIS"
    id = "ISO3166-A3_2_CTY"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{provider}/{id}/{version}"


@pytest.fixture()
def body():
    with open("tests/fmr/samples/map/code_map.json", "rb") as f:
        return f.read()


def test_returns_code_map(respx_mock, fmr, query, body):
    """get_code_map() should return a list of code mappings."""
    checks.check_code_mapping_core(respx_mock, fmr, query, body)


@pytest.mark.asyncio()
async def test_mapping_details(respx_mock, async_fmr, query, body):
    """The response contains the expected mappings."""
    await checks.check_code_mapping_details(respx_mock, async_fmr, query, body)
