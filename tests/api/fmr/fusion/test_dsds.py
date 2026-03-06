import pytest

import tests.api.fmr.dsd_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/", StructureFormat.FUSION_JSON
    )


@pytest.fixture
def async_fmr():
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2", StructureFormat.FUSION_JSON
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
def query_no_measure(fmr):
    res = "/structure/datastructure/"
    agency = "TEST"
    id = "NM_DSD"
    version = "1.0"
    return (
        f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"
        "?detail=referencepartial&references=descendants"
    )


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/dsd/dsd.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture
def body_partial_cs():
    with open(
        "tests/api/fmr/samples/dsd/dsd_partial_cs.fusion.json", "rb"
    ) as f:
        return f.read()


@pytest.fixture
def body_mm():
    with open("tests/api/fmr/samples/dsd/multi_meas.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture
def body_no_measure():
    with open(
        "tests/api/fmr/samples/dsd/dsd_no_measure.fusion.json", "rb"
    ) as f:
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


def test_no_measures(respx_mock, fmr, query_no_measure, body_no_measure):
    """Observation-level attributes work in measureless DSDs."""
    checks.check_measureless_dsd(
        respx_mock, fmr, query_no_measure, body_no_measure
    )
