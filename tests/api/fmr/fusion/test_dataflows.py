import pytest
import tests.api.fmr.dataflow_checks as checks

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
    res = "/structure/dataflow"
    all = "*"
    latest = "~"
    return f"{fmr.api_endpoint}{res}/{all}/{all}/{latest}"


@pytest.fixture()
def body():
    with open("tests/api/fmr/samples/df/flows.fusion.json", "rb") as f:
        return f.read()


def test_returns_dataflows(respx_mock, fmr, query, body):
    """get_dataflows() should return a collection of dataflows."""
    checks.check_dfrefs(respx_mock, fmr, query, body)


@pytest.mark.asyncio()
async def test_returns_dataflows_async(respx_mock, async_fmr, query, body):
    """get_dataflows() should return a collection of dataflows (async)."""
    await checks.check_dfrefs_async(respx_mock, async_fmr, query, body)
