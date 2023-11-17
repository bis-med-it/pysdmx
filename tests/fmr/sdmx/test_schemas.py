import pytest
import tests.fmr.schema_checks as checks

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
def query(fmr):
    res = "schema/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"


@pytest.fixture()
def no_const_query(fmr):
    res = "schema/datastructure/"
    agency = "BIS"
    id = "BIS_CBS"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"


@pytest.fixture()
def body():
    with open("tests/fmr/samples/df/schema.json", "rb") as f:
        return f.read()


@pytest.fixture()
def no_const_body():
    with open("tests/fmr/samples/df/no_const.json", "rb") as f:
        return f.read()


@pytest.fixture()
def no_measure_body():
    with open("tests/fmr/samples/df/no_measure.schema.json", "rb") as f:
        return f.read()


@pytest.fixture()
def no_attr_body():
    with open("tests/fmr/samples/df/no_attr.schema.json", "rb") as f:
        return f.read()


def test_returns_validation_context(respx_mock, fmr, query, body):
    """get_validation_context() should return a schema."""
    checks.check_schema(respx_mock, fmr, query, body)


@pytest.mark.asyncio()
async def test_codes(respx_mock, async_fmr, query, body):
    """Components have the expected number of codes."""
    await checks.check_coded_components(respx_mock, async_fmr, query, body)


def test_codes_no_const(respx_mock, fmr, no_const_query, no_const_body):
    """Components have the expected number of codes."""
    checks.check_unconstrained_coded_components(
        respx_mock, fmr, no_const_query, no_const_body
    )


def test_core_local_repr(respx_mock, fmr, no_const_query, no_const_body):
    """Components have the expected representation (local or core)."""
    checks.check_core_local_repr(
        respx_mock,
        fmr,
        no_const_query,
        no_const_body,
    )


def test_roles(respx_mock, fmr, query, body):
    """Components have the expected role."""
    checks.check_roles(respx_mock, fmr, query, body)


def test_types(respx_mock, fmr, query, body):
    """Components have the expected type."""
    checks.check_types(respx_mock, fmr, query, body)


def test_facets(respx_mock, fmr, query, body):
    """Components have the expected facets."""
    checks.check_facets(respx_mock, fmr, query, body)


def test_required(respx_mock, fmr, query, body):
    """Components have the expected required flag."""
    checks.check_required(respx_mock, fmr, query, body)


def test_attachment_level(respx_mock, fmr, query, body):
    """Components have the expected attachment level."""
    checks.check_attachment_level(respx_mock, fmr, query, body)


def test_description(respx_mock, fmr, query, body):
    """Components have the expected description."""
    checks.check_description(respx_mock, fmr, query, body)


def test_array_def(respx_mock, fmr, query, body):
    """Array components may have a min & max number of items."""
    checks.check_array_definition(respx_mock, fmr, query, body)


def test_no_measure(respx_mock, fmr, query, no_measure_body):
    """DSD may not contain any measure."""
    checks.check_no_measure(respx_mock, fmr, query, no_measure_body)


def test_no_attr(respx_mock, fmr, query, no_attr_body):
    """DSD may not contain any attribute."""
    checks.check_no_attrs(respx_mock, fmr, query, no_attr_body)
