import gzip

import httpx
import pytest

from pysdmx.api.qb import (
    ApiVersion,
    AsyncRestService,
    DataContext,
    DataQuery,
    RestService,
)
from pysdmx.errors import Unavailable


@pytest.fixture
def version() -> ApiVersion:
    return ApiVersion.V2_0_0


@pytest.fixture
def end_point() -> str:
    return "https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0"


@pytest.fixture
def query() -> DataQuery:
    return DataQuery(DataContext.DATAFLOW, "ESTAT", "UNE_RT_A")


@pytest.fixture
def url(end_point: str, query: DataQuery, version: ApiVersion) -> str:
    return f"{end_point}{query.get_url(version, True)}/"


@pytest.fixture
def body():
    with open("tests/api/fmr/samples/orgs/agencies.fusion.json", "rb") as f:
        return f.read()


@pytest.mark.parametrize("method", ["data", "stream_data"])
def test_gzip_body(respx_mock, end_point, version, query, url, body, method):
    # The body is gzipped without Content-Encoding, as Eurostat sends it
    compressed = gzip.compress(body)
    respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=compressed)
    )
    service = RestService(end_point, version)

    if method == "data":
        assert service.data(query) == body
    else:
        # Chunks of one byte split the gzip magic number
        chunks = list(service.stream_data(query, chunk_size=1))
        assert all(chunks)
        assert b"".join(chunks) == body


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["data", "stream_data"])
async def test_gzip_body_async(
    respx_mock, end_point, version, query, url, body, method
):
    compressed = gzip.compress(body)
    respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=compressed)
    )
    service = AsyncRestService(end_point, version)

    if method == "data":
        assert await service.data(query) == body
    else:
        chunks = [c async for c in service.stream_data(query, chunk_size=1)]
        assert all(chunks)
        assert b"".join(chunks) == body


def test_body_shorter_than_gzip_magic(
    respx_mock, end_point, version, query, url
):
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=b"x"))

    assert RestService(end_point, version).data(query) == b"x"


@pytest.mark.asyncio
async def test_body_shorter_than_gzip_magic_async(
    respx_mock, end_point, version, query, url
):
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=b"x"))
    service = AsyncRestService(end_point, version)

    chunks = [c async for c in service.stream_data(query)]

    assert chunks == [b"x"]


@pytest.mark.parametrize(
    "content",
    [
        # Truncated
        gzip.compress(b"<message/>" * 100)[:-10],
        # The gzip magic number, then an unknown compression method
        b"\x1f\x8b" + bytes(20),
    ],
)
def test_invalid_gzip_body(
    respx_mock, end_point, version, query, url, content
):
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=content))

    with pytest.raises(Unavailable):
        RestService(end_point, version).data(query)
