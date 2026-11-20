import pytest

import tests.api.fmr.data_constraint_checks as checks
from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient, StructureFormat


@pytest.fixture
def fmr() -> RegistryClient:
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2", StructureFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def async_fmr() -> AsyncRegistryClient:
    return AsyncRegistryClient(
        "https://registry.sdmx.org/sdmx/v2", StructureFormat.SDMX_JSON_2_0_0
    )


@pytest.fixture
def query(fmr: RegistryClient) -> str:
    return (
        f"{fmr.api_endpoint}/structure/dataconstraint/BIS.CBS/CBS_CONSTRAINTS/"
    )


@pytest.fixture
def query_ks(fmr: RegistryClient) -> str:
    return f"{fmr.api_endpoint}/structure/dataconstraint/BIS.CBS/AL/"


@pytest.fixture
def body() -> bytes:
    with open(
        "tests/api/fmr/samples/constraint/data_constraint.json", "rb"
    ) as file:
        return file.read()


@pytest.fixture
def body_ks() -> bytes:
    with open(
        "tests/api/fmr/samples/constraint/keyset_constraint.json", "rb"
    ) as file:
        return file.read()


def test_returns_data_constraint(respx_mock, fmr, query, body) -> None:
    """get_data_constraint() should return a data constraint."""
    checks.check_data_constraint(
        respx_mock,
        fmr,
        query,
        body,
        "BIS.CBS",
        "CBS_CONSTRAINTS",
        (("CBS_BANK_TYPE", ("4C", "4D")),),
    )


@pytest.mark.asyncio
async def test_returns_data_constraint_async(
    respx_mock, async_fmr, query, body
) -> None:
    """get_data_constraint() should return a data constraint asynchronously."""
    await checks.check_data_constraint_async(
        respx_mock,
        async_fmr,
        query,
        body,
        "BIS.CBS",
        "CBS_CONSTRAINTS",
        (("CBS_BANK_TYPE", ("4C", "4D")),),
    )


def test_returns_keyset_constraint(respx_mock, fmr, query_ks, body_ks) -> None:
    """get_data_constraint() should return a data constraint."""
    checks.check_keyset_constraint(
        respx_mock, fmr, query_ks, body_ks, "BIS.CBS", "AL"
    )
