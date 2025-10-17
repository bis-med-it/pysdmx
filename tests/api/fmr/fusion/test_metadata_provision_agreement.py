import pytest

import tests.api.fmr.mpa_checks as checks
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
    res = "/structure/metadataprovisionagreement/"
    agency = "TEST"
    id = "DF_CNF_SDMX_TEST"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/1.0/"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/pa/mpa.fusion.json", "rb") as f:
        return f.read()


def test_returns_provision_agreement(respx_mock, fmr, query, body):
    """get_metadata_provision_agreement() should return an mpa."""
    checks.check_metadata_provision_agreements(
        respx_mock, fmr, query, body, True
    )


@pytest.mark.asyncio
async def test_returns_provision_agreement_async(
    respx_mock, async_fmr, query, body
):
    """get_metadata_provision_agreement() should return an mpa, async."""
    await checks.check_metadata_provision_agreements_async(
        respx_mock, async_fmr, query, body
    )
