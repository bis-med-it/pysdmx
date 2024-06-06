import pytest
import tests.fmr.code_checks as checks

from pysdmx.api.fmr import AsyncRegistryClient, Format, RegistryClient


@pytest.fixture()
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def async_fmr():
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def query(fmr):
    res = "structure/codelist/"
    agency = "SDMX"
    id = "CL_FREQ"
    version = "2.0"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"


@pytest.fixture()
def body():
    with open("tests/fmr/samples/code/freq.json", "rb") as f:
        return f.read()


def test_returns_codelist(respx_mock, fmr, query, body):
    """get_codelist() should return a codelist with the expected codes."""
    checks.check_codelist(respx_mock, fmr, query, body)


@pytest.mark.asyncio()
async def test_codes_have_core_info(respx_mock, async_fmr, query, body):
    """Codes must contain core information such as ID and name."""
    await checks.check_code_core_info(respx_mock, async_fmr, query, body)


def test_codes_have_details(respx_mock, fmr, query, body):
    """Codes may have extended information."""
    checks.check_code_details(respx_mock, fmr, query, body)
