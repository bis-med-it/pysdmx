import httpx
import pytest

from pysdmx.api.qb import (
    ApiVersion,
    AsyncRestService,
    SchemaContext,
    SchemaFormat,
    SchemaQuery,
)
from pysdmx.errors import InternalError, Invalid, NotFound, Unavailable


@pytest.fixture
def version() -> ApiVersion:
    return ApiVersion.V2_0_0


@pytest.fixture
def end_point() -> str:
    return "https://registry.sdmx.org/sdmx/v2"


@pytest.fixture
def service(end_point: str, version: ApiVersion) -> AsyncRestService:
    return AsyncRestService(end_point, version)


@pytest.fixture
def query() -> SchemaQuery:
    return SchemaQuery(SchemaContext.DATAFLOW, "BIS", "CBS", "1.0")


@pytest.fixture
def url(end_point: str, query: SchemaQuery, version: ApiVersion) -> str:
    return f"{end_point}{query.get_url(version, True)}"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/orgs/agencies.fusion.json", "rb") as f:
        return f.read()


@pytest.mark.asyncio
async def test_not_found(
    respx_mock, service: AsyncRestService, query: SchemaQuery, body, url
):
    respx_mock.get(url).mock(
        return_value=httpx.Response(
            404,
            content=body,
        )
    )

    with pytest.raises(NotFound) as e:
        await service.schema(query)
    assert e.value.title is not None
    assert e.value.description is not None
    assert url in e.value.description


@pytest.mark.asyncio
async def test_client_error(
    respx_mock, service: AsyncRestService, query: SchemaQuery, body, url
):
    respx_mock.get(url).mock(
        return_value=httpx.Response(
            409,
            content=body,
        )
    )

    with pytest.raises(Invalid) as e:
        await service.schema(query)
    assert e.value.title is not None
    assert e.value.description is not None
    assert url in e.value.description


@pytest.mark.asyncio
async def test_service_error(
    respx_mock, service: AsyncRestService, query: SchemaQuery, body, url
):
    respx_mock.get(url).mock(
        return_value=httpx.Response(
            501,
            content=body,
        )
    )

    with pytest.raises(InternalError) as e:
        await service.schema(query)
    assert e.value.title is not None
    assert e.value.description is not None
    assert url in e.value.description


@pytest.mark.asyncio
async def test_service_unavailable(
    respx_mock, service: AsyncRestService, query: SchemaQuery, url
):
    re = httpx.RequestError("Bad day")
    respx_mock.get(url).mock(side_effect=re)

    with pytest.raises(Unavailable) as e:
        await service.schema(query)
    assert e.value.title is not None
    assert e.value.description is not None
    assert url in e.value.description


@pytest.mark.asyncio
async def test_called_as_expected(
    respx_mock, service: AsyncRestService, query: SchemaQuery, url, body
):
    route = respx_mock.get(url).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )
    await service.schema(query)
    assert route.called
    assert len(route.calls) == 1
    headers = route.calls[0].request.headers
    assert headers["Accept"] == SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE.value
    assert headers["Accept-Encoding"] == "gzip, deflate"
