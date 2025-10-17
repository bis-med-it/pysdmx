import pytest

import tests.api.fmr.metadata_provider_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2",
        StructureFormat.FUSION_JSON,
    )


@pytest.fixture
def async_fmr():
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        StructureFormat.FUSION_JSON,
    )


@pytest.fixture
def query(fmr: RegistryClient):
    res = "/structure/metadataproviderscheme/"
    agency = "BIS"
    return f"{fmr.api_endpoint}{res}{agency}/"


@pytest.fixture
def flowquery(fmr: RegistryClient):
    res = "/structure/metadataproviderscheme/"
    agency = "BIS"
    return (
        f"{fmr.api_endpoint}{res}{agency}"
        "?references=metadataprovisionagreement"
    )


@pytest.fixture
def body():
    with open(
        "tests/api/fmr/samples/orgs/metadata_providers.fusion.json", "rb"
    ) as f:
        return f.read()


@pytest.fixture
def flowbody():
    with open(
        "tests/api/fmr/samples/orgs/metadataprovidersflows.fusion.json", "rb"
    ) as f:
        return f.read()


def test_returns_metadata_providers(respx_mock, fmr, query, body):
    """get_metadata_providers() returns a collection of organizations."""
    checks.check_orgs(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_providers_have_core_info(respx_mock, async_fmr, query, body):
    """Metadata providers contain core information such as ID, name, etc."""
    await checks.check_org_core_info(respx_mock, async_fmr, query, body)


def test_providers_with_flows(respx_mock, fmr, flowquery, flowbody):
    """Metadata providers may have a list of metadataflows."""
    checks.check_with_flows(respx_mock, fmr, flowquery, flowbody)
