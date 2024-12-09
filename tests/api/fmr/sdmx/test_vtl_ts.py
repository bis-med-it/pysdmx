import pytest
import tests.api.fmr.vtl_ts_checks as checks

from pysdmx.api.fmr import AsyncRegistryClient, Format, RegistryClient


@pytest.fixture()
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def query(fmr):
    res = "/structure/transformationscheme/"
    provider = "TEST"
    id = "TEST_TS"
    version = "1.0"
    qst = "references=descendants&detail=referencepartial"
    return f"{fmr.api_endpoint}{res}{provider}/{id}/{version}?{qst}"


@pytest.fixture()
def body():
    with open("tests/api/fmr/samples/vtl/ts.json", "rb") as f:
        return f.read()


@pytest.fixture()
def body_cl():
    with open("tests/api/fmr/samples/vtl/tscl.json", "rb") as f:
        return f.read()


@pytest.fixture()
def body_cs():
    with open("tests/api/fmr/samples/vtl/tscs.json", "rb") as f:
        return f.read()


def test_returns_transformation_scheme(respx_mock, fmr, query, body):
    """get_vtl_transformation_scheme() returns a transformation scheme."""
    checks.check_transformation_scheme(respx_mock, fmr, query, body)


@pytest.mark.asyncio()
async def test_returns_transformation_scheme_async(
    respx_mock, async_fmr, query, body
):
    """The mapping definition contains the expected mapping rules."""
    await checks.check_transformation_scheme_async(
        respx_mock, async_fmr, query, body
    )


def test_vtl_codelist_mapping(respx_mock, fmr, query, body_cl):
    """get_vtl_transformation_scheme() suports codelist mapping."""
    checks.check_cl_mapping(respx_mock, fmr, query, body_cl)


def test_vtl_concept_mapping(respx_mock, fmr, query, body_cs):
    """get_vtl_transformation_scheme() supports concept mapping."""
    checks.check_concept_mapping(respx_mock, fmr, query, body_cs)
