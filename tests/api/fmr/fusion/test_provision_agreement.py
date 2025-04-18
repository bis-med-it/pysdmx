import pytest

import tests.api.fmr.pa_checks as checks
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
    res = "/structure/provisionagreement/"
    agency = "BIS.CBS"
    id = "CBS_BIS_5B0"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/1.0"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/pa/pa.fusion.json", "rb") as f:
        return f.read()


def test_returns_provision_agreement(respx_mock, fmr, query, body):
    """get_provision_agreement() should return a provision agreement."""
    checks.check_provision_agreements(respx_mock, fmr, query, body, True)


@pytest.mark.asyncio
async def test_returns_provision_agreement_async(
    respx_mock, async_fmr, query, body
):
    """get_provision_agreement() should return a provision agreement, async."""
    await checks.check_provision_agreements_async(
        respx_mock, async_fmr, query, body
    )
