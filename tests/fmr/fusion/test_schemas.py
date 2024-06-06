import httpx
import pytest
import tests.fmr.schema_checks as checks

from pysdmx.api.fmr import AsyncRegistryClient, Format, RegistryClient
from pysdmx.errors import ServiceError


@pytest.fixture()
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.FUSION_JSON,
    )


@pytest.fixture()
def async_fmr():
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        Format.FUSION_JSON,
    )


@pytest.fixture()
def query(fmr):
    res = "schema/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"


@pytest.fixture()
def query_pra(fmr):
    res = "schema/provisionagreement/"
    agency = "BIS.CBS"
    id = "CBS_BIS_GR2"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"


@pytest.fixture()
def no_hca_query(fmr):
    res = "structure/dataflow/"
    agency = "BIS.CBS"
    id = "CBS"
    version = "1.0"
    return (
        f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"
        "?references=all&detail=referencepartial"
    )


@pytest.fixture()
def no_hca_pra_query(fmr):
    res = "structure/provisionagreement/"
    agency = "BIS.CBS"
    id = "CBS_BIS_GR2"
    version = "1.0"
    return (
        f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"
        "?references=all&detail=referencepartial"
    )


@pytest.fixture()
def hierarchy_hca_query(fmr):
    res = "structure/dataflow/"
    agency = "BIS"
    id = "TEST_DF"
    version = "1.0"
    return (
        f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"
        "?references=all&detail=referencepartial"
    )


@pytest.fixture()
def hierarchy_hca_query_pra(fmr):
    res = "structure/provisionagreement/"
    agency = "BIS.CBS"
    id = "CBS_BIS_TEST"
    version = "1.0"
    return (
        f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"
        "?references=all&detail=referencepartial"
    )


@pytest.fixture()
def hierarchy_query(fmr):
    res = "schema/dataflow/"
    agency = "BIS"
    id = "TEST_DF"
    version = "1.0"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/{version}"


@pytest.fixture()
def hierarchy_query_pra(fmr):
    res = "schema/provisionagreement/"
    agency = "BIS.CBS"
    id = "CBS_BIS_TEST"
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
    with open("tests/fmr/samples/df/schema.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def body_from_pra():
    with open("tests/fmr/samples/pra/schema.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def no_const_body():
    with open("tests/fmr/samples/df/no_const.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def no_measure_body():
    with open("tests/fmr/samples/df/no_measure.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def no_attr_body():
    with open("tests/fmr/samples/df/no_attr.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def error_body():
    with open("tests/fmr/samples/df/errorlvl.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def hierarchy_body():
    with open("tests/fmr/samples/df/hierarchy_schema.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def hier_assoc_body():
    with open("tests/fmr/samples/df/hierarchy_hca.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def hierarchy_pra_body():
    with open("tests/fmr/samples/pra/hierarchy_schema.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def hier_assoc_pra_body():
    with open("tests/fmr/samples/pra/hierarchy_hca.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def no_hca_body():
    with open("tests/fmr/samples/df/no_hca.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def no_hca_pra_body():
    with open("tests/fmr/samples/pra/no_hca.fusion.json", "rb") as f:
        return f.read()


def test_returns_validation_context(
    respx_mock, fmr, query, no_hca_query, body, no_hca_body
):
    """get_validation_context() should return a schema."""
    checks.check_schema(
        respx_mock, fmr, query, no_hca_query, body, no_hca_body
    )


def test_returns_pra_validation_context(
    respx_mock,
    fmr,
    query_pra,
    no_hca_pra_query,
    body_from_pra,
    no_hca_pra_body,
):
    """get_validation_context() should return a schema."""
    checks.check_schema_from_pra(
        respx_mock,
        fmr,
        query_pra,
        no_hca_pra_query,
        body_from_pra,
        no_hca_pra_body,
    )


@pytest.mark.asyncio()
async def test_codes(
    respx_mock, async_fmr, query, no_hca_query, body, no_hca_body
):
    """Components have the expected number of codes."""
    await checks.check_coded_components(
        respx_mock, async_fmr, query, no_hca_query, body, no_hca_body
    )


@pytest.mark.asyncio()
async def test_codes_pra(
    respx_mock,
    async_fmr,
    query_pra,
    no_hca_pra_query,
    body_from_pra,
    no_hca_pra_body,
):
    """Components have the expected number of codes."""
    await checks.check_coded_pra_components(
        respx_mock,
        async_fmr,
        query_pra,
        no_hca_pra_query,
        body_from_pra,
        no_hca_pra_body,
    )


@pytest.mark.asyncio()
async def test_core_local_repr_async(
    respx_mock,
    async_fmr,
    no_const_query,
    no_hca_query,
    no_const_body,
    no_hca_body,
):
    """Components have the expected representation (local or core)."""
    await checks.check_core_local_repr_async(
        respx_mock,
        async_fmr,
        no_const_query,
        no_hca_query,
        no_const_body,
        no_hca_body,
    )


def test_codes_no_const(
    respx_mock, fmr, no_const_query, no_hca_query, no_const_body, no_hca_body
):
    """Components have the expected number of codes."""
    checks.check_unconstrained_coded_components(
        respx_mock,
        fmr,
        no_const_query,
        no_hca_query,
        no_const_body,
        no_hca_body,
    )


def test_core_local_repr(
    respx_mock, fmr, no_const_query, no_hca_query, no_const_body, no_hca_body
):
    """Components have the expected representation (local or core)."""
    checks.check_core_local_repr(
        respx_mock,
        fmr,
        no_const_query,
        no_hca_query,
        no_const_body,
        no_hca_body,
    )


def test_roles(respx_mock, fmr, query, no_hca_query, body, no_hca_body):
    """Components have the expected role."""
    checks.check_roles(respx_mock, fmr, query, no_hca_query, body, no_hca_body)


def test_types(respx_mock, fmr, query, no_hca_query, body, no_hca_body):
    """Components have the expected type."""
    checks.check_types(respx_mock, fmr, query, no_hca_query, body, no_hca_body)


def test_facets(respx_mock, fmr, query, no_hca_query, body, no_hca_body):
    """Components have the expected facets."""
    checks.check_facets(
        respx_mock, fmr, query, no_hca_query, body, no_hca_body
    )


def test_required(respx_mock, fmr, query, no_hca_query, body, no_hca_body):
    """Components have the expected required flag."""
    checks.check_required(
        respx_mock, fmr, query, no_hca_query, body, no_hca_body
    )


def test_attachment_level(
    respx_mock, fmr, query, no_hca_query, body, no_hca_body
):
    """Components have the expected attachment level."""
    checks.check_attachment_level(
        respx_mock, fmr, query, no_hca_query, body, no_hca_body
    )


def test_error_level(
    respx_mock, fmr, query, no_hca_query, error_body, no_hca_body
):
    """Attachment level could not be inferred."""
    respx_mock.get(no_hca_query).mock(
        return_value=httpx.Response(
            200,
            content=no_hca_body,
        )
    )
    respx_mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=error_body,
        )
    )

    with pytest.raises(
        ServiceError,
        match="Could not infer attribute attachment level",
    ):
        fmr.get_schema(
            "dataflow",
            "BIS.CBS",
            "CBS",
            "1.0",
        )


def test_description(respx_mock, fmr, query, no_hca_query, body, no_hca_body):
    """Components have the expected description."""
    checks.check_description(
        respx_mock, fmr, query, no_hca_query, body, no_hca_body
    )


def test_array_def(respx_mock, fmr, query, no_hca_query, body, no_hca_body):
    """Array components may have a min & max number of items."""
    checks.check_array_definition(
        respx_mock, fmr, query, no_hca_query, body, no_hca_body
    )


def test_no_measure(
    respx_mock, fmr, query, no_hca_query, no_measure_body, no_hca_body
):
    """DSD may not contain any measure."""
    checks.check_no_measure(
        respx_mock, fmr, query, no_hca_query, no_measure_body, no_hca_body
    )


def test_no_attr(
    respx_mock, fmr, query, no_hca_query, no_attr_body, no_hca_body
):
    """DSD may not contain any attribute."""
    checks.check_no_attrs(
        respx_mock, fmr, query, no_hca_query, no_attr_body, no_hca_body
    )


def test_has_hierarchy(
    respx_mock,
    fmr,
    hierarchy_query,
    hierarchy_hca_query,
    hierarchy_body,
    hier_assoc_body,
):
    """Components may reference a hierarchy."""
    checks.check_hierarchy(
        respx_mock,
        fmr,
        hierarchy_query,
        hierarchy_hca_query,
        hierarchy_body,
        hier_assoc_body,
    )


def test_has_hierarchy_pra(
    respx_mock,
    fmr,
    hierarchy_query_pra,
    hierarchy_hca_query_pra,
    hierarchy_pra_body,
    hier_assoc_pra_body,
):
    """Components may reference a hierarchy."""
    checks.check_hierarchy_pra(
        respx_mock,
        fmr,
        hierarchy_query_pra,
        hierarchy_hca_query_pra,
        hierarchy_pra_body,
        hier_assoc_pra_body,
    )
