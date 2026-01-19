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
def query_mm(fmr):
    res = "/structure/datastructure/"
    agency = "TEST"
    id = "TEST_MM"
    version = "1.0"
    return (
        f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"
        "?detail=referencepartial&references=descendants"
    )


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/dsd/dsd.json", "rb") as f:
        return f.read()


@pytest.fixture
def body_partial_cs():
    with open("tests/api/fmr/samples/dsd/dsd_partial_cs.json", "rb") as f:
        return f.read()


@pytest.fixture
def body_mm():
    with open("tests/api/fmr/samples/dsd/multi_meas.json", "rb") as f:
        return f.read()


def test_dsd(respx_mock, fmr, query, body):
    """get_data_structures() should return a DSD."""
    checks.check_dsd(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_dsd_async(respx_mock, async_fmr, query, body):
    """get_data_structures() should return a DSD (async)."""
    await checks.check_dsd_async(respx_mock, async_fmr, query, body)


def test_multiple_measures(respx_mock, fmr, query_mm, body_mm):
    """Multiple measures are extracted, including attachment level."""
    checks.check_multi_meas(respx_mock, fmr, query_mm, body_mm)


def test_dsd_partial_cs(respx_mock, fmr, query, body_partial_cs):
    """get_data_structures() returns a DSD even if concepts are missing."""
    checks.check_dsd_partial_cs(respx_mock, fmr, query, body_partial_cs)
