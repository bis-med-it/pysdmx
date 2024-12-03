import pytest

from pysdmx.api.fmr import AsyncRegistryClient, Format, RegistryClient
import tests.api.fmr.hierarchy_checks as checks


@pytest.fixture
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.FUSION_JSON,
    )


@pytest.fixture
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.FUSION_JSON,
    )


@pytest.fixture
def query(fmr):
    res = "/structure/hierarchy/"
    agency = "TEST"
    id = "HCL_ELEMENT"
    qst = "detail=referencepartial&references=codelist"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/+?{qst}"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/code/hier.fusion.json", "rb") as f:
        return f.read()


def test_returns_hierarchy(respx_mock, fmr, query, body):
    """get_hierarchy() should return a hierarchy."""
    checks.check_hierarchy(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_hcode_have_core_info(respx_mock, async_fmr, query, body):
    """Hierarchical codes contain core information such as ID and name."""
    await checks.check_hcode_core_info(respx_mock, async_fmr, query, body)


def test_hcode_have_details(respx_mock, fmr, query, body):
    """Hierarchical codes may have extended information."""
    checks.check_hcode_details(respx_mock, fmr, query, body)
