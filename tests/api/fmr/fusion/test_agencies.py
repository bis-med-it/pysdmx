import pytest
import tests.api.fmr.agency_checks as checks

from pysdmx.api.fmr import AsyncRegistryClient, Format, RegistryClient


@pytest.fixture()
def fmr() -> RegistryClient:
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2",
        Format.FUSION_JSON,
    )


@pytest.fixture()
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.FUSION_JSON,
    )


@pytest.fixture()
def query(fmr: RegistryClient) -> str:
    res = "/structure/agencyscheme/"
    agency = "BIS"
    return f"{fmr.api_endpoint}{res}{agency}"


@pytest.fixture()
def body():
    with open("tests/api/fmr/samples/orgs/agencies.fusion.json", "rb") as f:
        return f.read()


def test_returns_orgs(respx_mock, fmr, query, body):
    """get_agencies() should return a collection of organizations."""
    checks.check_orgs(respx_mock, fmr, query, body)


@pytest.mark.asyncio()
async def test_orgs_have_core_info(respx_mock, async_fmr, query, body):
    """Agencies must contain core information such as ID and name."""
    await checks.check_org_core_info(respx_mock, async_fmr, query, body)


def test_detailed_orgs(respx_mock, fmr, query, body):
    """Agencies may have contact information."""
    checks.check_org_details(respx_mock, fmr, query, body)
