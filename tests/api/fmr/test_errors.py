import httpx
import pytest

from pysdmx.api.fmr import Format, RegistryClient
from pysdmx.errors import InternalError, Invalid, NotFound, Unavailable


@pytest.fixture()
def fmr() -> RegistryClient:
    return RegistryClient(
        "https://registry.sdmx.org/sdmx/v2",
        Format.SDMX_JSON,
    )


@pytest.fixture()
def query(fmr: RegistryClient) -> str:
    res = "/structure/agencyscheme/"
    agency = "BIS"
    return f"{fmr.api_endpoint}{res}{agency}"


@pytest.fixture()
def body():
    with open("tests/api/fmr/samples/orgs/agencies.fusion.json", "rb") as f:
        return f.read()


def test_not_found(respx_mock, fmr, query, body):
    respx_mock.get(query).mock(
        return_value=httpx.Response(
            404,
            content=body,
        )
    )

    with pytest.raises(NotFound) as e:
        fmr.get_agencies("BIS")
    assert e.value.title is not None
    assert e.value.description is not None
    assert query in e.value.description


def test_client_error(respx_mock, fmr, query, body):
    respx_mock.get(query).mock(
        return_value=httpx.Response(
            409,
            content=body,
        )
    )

    with pytest.raises(Invalid) as e:
        fmr.get_agencies("BIS")
    assert e.value.title is not None
    assert e.value.description is not None
    assert query in e.value.description


def test_service_error(respx_mock, fmr, query, body):
    respx_mock.get(query).mock(
        return_value=httpx.Response(
            501,
            content=body,
        )
    )

    with pytest.raises(InternalError) as e:
        fmr.get_agencies("BIS")
    assert e.value.title is not None
    assert e.value.description is not None
    assert query in e.value.description


def test_service_unavailable(respx_mock, fmr, query):
    re = httpx.RequestError("Bad day")
    respx_mock.get(query).mock(side_effect=re)

    with pytest.raises(Unavailable) as e:
        fmr.get_agencies("BIS")
    assert e.value.title is not None
    assert e.value.description is not None
    assert query in e.value.description


def test_missing_params(fmr):
    with pytest.raises(Invalid) as e:
        fmr.get_agencies(42)
    assert e.value.title is not None
    assert e.value.description is not None
