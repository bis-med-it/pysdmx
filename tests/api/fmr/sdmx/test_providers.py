import pytest

import tests.api.fmr.provider_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/", StructureFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def async_fmr():
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2", StructureFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def query(fmr: RegistryClient):
    res = "/structure/dataproviderscheme/"
    agency = "BIS"
    return f"{fmr.api_endpoint}{res}{agency}"


@pytest.fixture
def flowquery(fmr: RegistryClient):
    res = "/structure/dataproviderscheme/"
    agency = "BIS"
    return f"{fmr.api_endpoint}{res}{agency}?references=provisionagreement"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/orgs/providers.json", "rb") as f:
        return f.read()


@pytest.fixture
def empty():
    with open("tests/api/fmr/samples/orgs/empty_providers.json", "rb") as f:
        return f.read()


@pytest.fixture
def flowbody():
    with open("tests/api/fmr/samples/orgs/providersflows.json", "rb") as f:
        return f.read()


def test_returns_providers(respx_mock, fmr, query, body):
    """get_providers() should return a collection of organizations."""
    checks.check_orgs(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_providers_have_core_info(respx_mock, async_fmr, query, body):
    """Providers must contain core information such as ID, name, etc."""
    await checks.check_org_core_info(respx_mock, async_fmr, query, body)


def test_detailed_providers(respx_mock, fmr, query, body):
    """Providers may have contact information."""
    checks.check_org_details(respx_mock, fmr, query, body)


def test_providers_with_flows(respx_mock, fmr, flowquery, flowbody):
    """Providers may have contact information."""
    checks.check_with_flows(respx_mock, fmr, flowquery, flowbody)


def test_empty_orgs(respx_mock, fmr, query, empty):
    """Can handle empty schemes."""
    checks.check_empty(respx_mock, fmr, query, empty)
