import pytest

import tests.api.fmr.agency_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr() -> RegistryClient:
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2", StructureFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def fmr20() -> RegistryClient:
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2",
        StructureFormat.SDMX_JSON_2_0_0,
        timeout=20.0,
    )


@pytest.fixture
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2", StructureFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def query(fmr: RegistryClient) -> str:
    res = "/structure/agencyscheme/"
    agency = "BIS"
    return f"{fmr.api_endpoint}{res}{agency}"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/orgs/agencies.json", "rb") as f:
        return f.read()


@pytest.fixture
def empty():
    with open("tests/api/fmr/samples/orgs/empty_agencies.json", "rb") as f:
        return f.read()


def test_returns_orgs(respx_mock, fmr, query, body):
    """get_agencies() should return a collection of organizations."""
    checks.check_orgs(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_orgs_have_core_info(respx_mock, async_fmr, query, body):
    """Agencies must contain core information such as ID and name."""
    await checks.check_org_core_info(respx_mock, async_fmr, query, body)


def test_detailed_orgs(respx_mock, fmr20, query, body):
    """Agencies may have contact information."""
    checks.check_org_details(respx_mock, fmr20, query, body)


def test_empty_orgs(respx_mock, fmr, query, empty):
    """get_agencies() can handle empty schemes."""
    checks.check_empty(respx_mock, fmr, query, empty)
