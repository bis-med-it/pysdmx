import pytest
import tests.api.fmr.category_checks as checks

from pysdmx.api.fmr import AsyncRegistryClient, Format, RegistryClient


@pytest.fixture()
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.FUSION_JSON,
    )


@pytest.fixture()
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2",
        Format.FUSION_JSON,
    )


@pytest.fixture()
def query(fmr):
    res = "/structure/categoryscheme/"
    agency = "TEST"
    id = "TEST_CS"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/+"


@pytest.fixture()
def body():
    with open("tests/api/fmr/samples/cat/cs.fusion.json", "rb") as f:
        return f.read()


def test_returns_categories(respx_mock, fmr, query, body):
    """get_categories() should return a category scheme."""
    checks.check_categories(respx_mock, fmr, query, body)


@pytest.mark.asyncio()
async def test_categories_have_core_info(respx_mock, async_fmr, query, body):
    """Categories must contain core information such as ID and name."""
    await checks.check_category_core_info(respx_mock, async_fmr, query, body)


def test_categories_have_details(respx_mock, fmr, query, body):
    """Categories may have extended information."""
    checks.check_category_details(respx_mock, fmr, query, body)
