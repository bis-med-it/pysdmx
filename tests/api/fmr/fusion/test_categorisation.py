import pytest

import tests.api.fmr.categorisation_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        StructureFormat.FUSION_JSON,
    )


@pytest.fixture
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        StructureFormat.FUSION_JSON,
    )


@pytest.fixture
def query(fmr):
    res = "/structure/categorisation/"
    agency = "TEST"
    id = "06E00965-AB55-F0C3-5CA3-9D454F3BE88F"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/1.0"


@pytest.fixture
def body():
    with open(
        "tests/api/fmr/samples/cat/categorisation.fusion.json", "rb"
    ) as f:
        return f.read()


def test_returns_categorisation(respx_mock, fmr, query, body):
    """get_categorisation() should return a categorisation."""
    checks.check_categorisations(respx_mock, fmr, query, body, True)


@pytest.mark.asyncio
async def test_returns_categorisation_async(
    respx_mock, async_fmr, query, body
):
    """get_categorisation() should return a categorisation (async)."""
    await checks.check_categorisations_async(
        respx_mock, async_fmr, query, body
    )
