import pytest

import tests.api.fmr.msds_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr() -> RegistryClient:
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2",
        StructureFormat.SDMX_JSON_2_0_0,
    )


@pytest.fixture
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        StructureFormat.SDMX_JSON_2_0_0,
    )


@pytest.fixture
def query(fmr: RegistryClient) -> str:
    res = "/structure/metadatastructure"
    all = "*"
    latest = "+"
    return (
        f"{fmr.api_endpoint}{res}/{all}/{all}/{latest}"
        "?references=descendants&detail=referencepartial"
    )


@pytest.fixture
def query_437(fmr: RegistryClient) -> str:
    res = "/structure/metadatastructure"
    agency = "ESTAT"
    id = "ACQUIS_COMPLIANCE_MSD"
    version = "1.2"
    return (
        f"{fmr.api_endpoint}{res}/{agency}/{id}/{version}"
        "?references=descendants&detail=referencepartial"
    )


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/refmeta/msd.json", "rb") as f:
        return f.read()


@pytest.fixture
def body_437():
    with open("tests/api/fmr/samples/refmeta/bug437.json", "rb") as f:
        return f.read()


def test_returns_msds(respx_mock, fmr, query, body):
    """get_metadata_structures should return a collection of MSDs."""
    checks.check_msds(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_returns_msds_async(respx_mock, async_fmr, query, body):
    """get_metadata_structures should return a collection of MSDs (async)."""
    await checks.check_msds_async(respx_mock, async_fmr, query, body)


def test_bug437(respx_mock, fmr, query_437, body_437):
    """Address bug 437."""
    checks.check_bug437(respx_mock, fmr, query_437, body_437)
