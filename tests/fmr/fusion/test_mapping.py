import pytest
import tests.fmr.mapping_checks as checks

from pysdmx.fmr import AsyncRegistryClient, Format, RegistryClient


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
def query1(fmr):
    res = "structure/structuremap/"
    provider = "BIS"
    id = "SRC_2_MDD"
    version = "1.0"
    qst = "references=children&detail=referencepartial"
    return f"{fmr.api_endpoint}{res}{provider}/{id}/{version}?{qst}"


@pytest.fixture()
def body1():
    with open("tests/fmr/samples/map/sm.fusion.json", "rb") as f:
        return f.read()


@pytest.fixture()
def query2(fmr):
    res = "structure/structuremap/"
    provider = "BIS"
    id = "FXS_2_MDD"
    version = "1.0"
    qst = "references=children&detail=referencepartial"
    return f"{fmr.api_endpoint}{res}{provider}/{id}/{version}?{qst}"


@pytest.fixture()
def body2():
    with open("tests/fmr/samples/map/multi.fusion.json", "rb") as f:
        return f.read()


def test_returns_mapping_definition(respx_mock, fmr, query1, body1):
    """get_mapping() should return a mapping definition."""
    checks.check_mapping(respx_mock, fmr, query1, body1)


def test_returns_multi_mapping_definition(respx_mock, fmr, query2, body2):
    """get_mapping() should return a mapping definition."""
    checks.check_multi_mapping(respx_mock, fmr, query2, body2)


@pytest.mark.asyncio()
async def test_mapping_rules(respx_mock, async_fmr, query1, body1):
    """The mapping definition contains the expected mapping rules."""
    await checks.check_mapping_rules(respx_mock, async_fmr, query1, body1)
