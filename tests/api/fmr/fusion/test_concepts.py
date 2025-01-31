import pytest

import tests.api.fmr.concept_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr():
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        StructureFormat.FUSION_JSON,
    )


@pytest.fixture
def async_fmr():
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2/",
        StructureFormat.FUSION_JSON,
    )


@pytest.fixture
def query(fmr):
    res = "/structure/conceptscheme/"
    agency = "BIS.MEDIT"
    id = "MEDIT_CS"
    return f"{fmr.api_endpoint}{res}{agency}/{id}/+?references=codelist"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/concept/cs.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture
def empty():
    with open("tests/api/fmr/samples/concept/empty_cs.fusion.json", "rb") as f:
        return f.read()


def test_returns_cs(respx_mock, fmr, query, body):
    """get_concepts() should return a concept scheme."""
    checks.check_cs(respx_mock, fmr, query, body)


@pytest.mark.asyncio
async def test_concepts_have_core_info(respx_mock, async_fmr, query, body):
    """Concepts must contain core information such as ID and name."""
    await checks.check_concept_core_info(respx_mock, async_fmr, query, body)


def test_concepts_have_details(respx_mock, fmr, query, body):
    """Concepts may have extended information."""
    checks.check_concept_details(respx_mock, fmr, query, body)


def test_empty(respx_mock, fmr, query, empty):
    """Can handle empty schemes."""
    checks.check_empty(respx_mock, fmr, query, empty)
