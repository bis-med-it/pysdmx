import pytest
import tests.api.fmr.mult_reports_checks as checks

from pysdmx.api.fmr import AsyncRegistryClient, Format, RegistryClient


@pytest.fixture()
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.FUSION_JSON,
    )


@pytest.fixture()
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.FUSION_JSON,
    )


@pytest.fixture()
def query(fmr):
    res = "metadata/structure/"
    typ = "dataflow"
    agency = "BIS.MACRO"
    id = "BIS_MACRO"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{typ}/{agency}/{id}/{version}"


@pytest.fixture()
def body():
    with open(
        "tests/api/fmr/samples/refmeta/mult_reports.fusion.json", "rb"
    ) as f:
        return f.read()


def test_returns_mult_report(respx_mock, fmr, query, body):
    """get_reports() should return multiple reports."""
    checks.check_reports(respx_mock, fmr, query, body)


@pytest.mark.asyncio()
async def test_returns_mult_report_async(respx_mock, async_fmr, query, body):
    """get_reports() should return multiple reports (async)."""
    await checks.check_reports_async(respx_mock, async_fmr, query, body)
