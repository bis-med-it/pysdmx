import pytest

import tests.api.fmr.dsd_checks as checks
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
def query(fmr):
    res = "/structure/datastructure/"
    agency = "BIS"
    id = "BIS_CBS"
    version = "1.0"
    return (
        f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"
        "?detail=referencepartial&references=descendants"
    )


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/dsd/dsd.json", "rb") as f:
        return f.read()


def test_dsd(respx_mock, fmr, query, body):
    """get_data_structures() should return a DSD."""
    checks.check_dsd(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_dsd_async(respx_mock, async_fmr, query, body):
    """get_data_structures() should return a DSD (async)."""
    await checks.check_dsd_async(respx_mock, async_fmr, query, body)
