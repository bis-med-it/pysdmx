import pytest

import tests.api.fmr.metadataflow_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr() -> RegistryClient:
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2",
        StructureFormat.FUSION_JSON,
    )


@pytest.fixture
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        StructureFormat.FUSION_JSON,
    )


@pytest.fixture
def query(fmr: RegistryClient) -> str:
    res = "/structure/metadataflow"
    all = "*"
    latest = "+"
    return f"{fmr.api_endpoint}{res}/{all}/{all}/{latest}"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/refmeta/mdf.fusion.json", "rb") as f:
        return f.read()


def test_returns_dataflows(respx_mock, fmr, query, body):
    """get_metadataflows() returns a collection of metadataflows."""
    checks.check_metadataflows(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_returns_dataflows_async(respx_mock, async_fmr, query, body):
    """get_metadataflows() return a collection of metadataflows (async)."""
    await checks.check_metadataflows_async(respx_mock, async_fmr, query, body)
