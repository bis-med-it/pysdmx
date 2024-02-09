import pytest
import tests.fmr.dataflow_checks as checks

from pysdmx.fmr import AsyncRegistryClient, Format, RegistryClient


@pytest.fixture()
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def async_fmr():
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def schema_query(fmr):
    res = "schema/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"


@pytest.fixture()
def schema_query_no_version(fmr):
    res = "schema/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "+"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"


@pytest.fixture()
def no_hca_query(fmr):
    res = "structure/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "1.0"
    return (
        f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"
        "?references=parentsandsiblings&detail=referencepartial"
    )


@pytest.fixture()
def no_hca_body():
    with open("tests/fmr/samples/df/no_hca.json", "rb") as f:
        return f.read()


@pytest.fixture()
def dataflow_query(fmr):
    res = "structure/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "1.0"
    qst = "detail=referencepartial&references=parentsandsiblings"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}?{qst}"


@pytest.fixture()
def dataflow_query_no_version(fmr):
    res = "structure/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "+"
    qst = "detail=referencepartial&references=parentsandsiblings"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}?{qst}"


@pytest.fixture()
def core_dataflow_query(fmr):
    res = "structure/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "1.0"
    qst = "detail=referencepartial&references=none"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}?{qst}"


@pytest.fixture()
def schema_body():
    with open("tests/fmr/samples/df/schema.json", "rb") as f:
        return f.read()


@pytest.fixture()
def dataflow_body():
    with open("tests/fmr/samples/df/details.json", "rb") as f:
        return f.read()


@pytest.fixture()
def core_dataflow_body():
    with open("tests/fmr/samples/df/details_core.json", "rb") as f:
        return f.read()


def test_returns_dataflow_info(
    respx_mock,
    fmr,
    schema_query,
    schema_body,
    dataflow_query,
    dataflow_body,
):
    """get_dataflow_details() should return information about a dataflow."""
    checks.check_dataflow_info(
        respx_mock,
        fmr,
        schema_query,
        schema_body,
        dataflow_query,
        dataflow_body,
    )


def test_returns_dataflow_no_version(
    respx_mock,
    fmr,
    schema_query_no_version,
    schema_body,
    dataflow_query_no_version,
    dataflow_body,
):
    """get_dataflow_details() return information about a dataflow (+)."""
    checks.check_dataflow_info_no_version(
        respx_mock,
        fmr,
        schema_query_no_version,
        schema_body,
        dataflow_query_no_version,
        dataflow_body,
    )


def test_returns_core_dataflow_info(
    respx_mock,
    fmr,
    core_dataflow_query,
    core_dataflow_body,
):
    """get_dataflow_details() should return information about a dataflow."""
    checks.check_core_dataflow_info(
        respx_mock,
        fmr,
        core_dataflow_query,
        core_dataflow_body,
    )


def test_returns_dataflow_with_provs(
    respx_mock,
    fmr,
    dataflow_query,
    dataflow_body,
):
    """get_dataflow_details() should return information about a dataflow."""
    checks.check_dataflow_info_with_provs(
        respx_mock,
        fmr,
        dataflow_query,
        dataflow_body,
    )


def test_returns_dataflow_info_with_schema(
    respx_mock,
    fmr,
    schema_query,
    schema_body,
    core_dataflow_query,
    core_dataflow_body,
    no_hca_query,
    no_hca_body,
):
    """get_dataflow_details() should return information about a dataflow."""
    checks.check_dataflow_info_with_schema(
        respx_mock,
        fmr,
        schema_query,
        schema_body,
        core_dataflow_query,
        core_dataflow_body,
        no_hca_query,
        no_hca_body,
    )


@pytest.mark.asyncio()
async def test_async_returns_dataflow_info(
    respx_mock,
    async_fmr,
    schema_query,
    schema_body,
    dataflow_query,
    dataflow_body,
    no_hca_query,
    no_hca_body,
):
    """get_dataflow_details() should return information about a dataflow."""
    await checks.check_async_dataflow_info(
        respx_mock,
        async_fmr,
        schema_query,
        schema_body,
        dataflow_query,
        dataflow_body,
        no_hca_query,
        no_hca_body,
    )


@pytest.mark.asyncio()
async def test_returns_async_core_dataflow_info(
    respx_mock,
    async_fmr,
    core_dataflow_query,
    core_dataflow_body,
):
    """get_dataflow_details() returns core details about a flow (async)."""
    await checks.check_async_core_dataflow_info(
        respx_mock,
        async_fmr,
        core_dataflow_query,
        core_dataflow_body,
    )
