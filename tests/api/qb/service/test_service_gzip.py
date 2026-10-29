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


def _fetch(end_point, version, query, method):
    """The body the service returns, checking it streams no empty chunk."""
    service = RestService(end_point, version)
    if method == "data":
        return service.data(query)
    # Chunks of one byte split the gzip magic number
    chunks = list(service.stream_data(query, chunk_size=1))
    assert all(chunks)
    return b"".join(chunks)


async def _afetch(end_point, version, query, method):
    """The body the service returns, checking it streams no empty chunk."""
    service = AsyncRestService(end_point, version)
    if method == "data":
        return await service.data(query)
    chunks = [c async for c in service.stream_data(query, chunk_size=1)]
    assert all(chunks)
    return b"".join(chunks)


@pytest.mark.parametrize("method", ["data", "stream_data"])
def test_gzip_body(respx_mock, end_point, version, query, url, body, method):
    # The body is gzipped without Content-Encoding, as Eurostat sends it
    compressed = gzip.compress(body)
    respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=compressed)
    )

    assert _fetch(end_point, version, query, method) == body


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["data", "stream_data"])
async def test_gzip_body_async(
    respx_mock, end_point, version, query, url, body, method
):
    compressed = gzip.compress(body)
    respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=compressed)
    )

    assert await _afetch(end_point, version, query, method) == body


@pytest.mark.parametrize("method", ["data", "stream_data"])
def test_body_shorter_than_gzip_magic(
    respx_mock, end_point, version, query, url, method
):
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=b"x"))

    assert _fetch(end_point, version, query, method) == b"x"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["data", "stream_data"])
async def test_body_shorter_than_gzip_magic_async(
    respx_mock, end_point, version, query, url, method
):
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=b"x"))

    assert await _afetch(end_point, version, query, method) == b"x"


@pytest.mark.parametrize("method", ["data", "stream_data"])
def test_truncated_gzip_body(
    respx_mock, end_point, version, query, url, body, method
):
    truncated = gzip.compress(body)[:-10]
    respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=truncated)
    )

    with pytest.raises(Unavailable, match="end-of-stream marker"):
        _fetch(end_point, version, query, method)


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["data", "stream_data"])
async def test_truncated_gzip_body_async(
    respx_mock, end_point, version, query, url, body, method
):
    truncated = gzip.compress(body)[:-10]
    respx_mock.get(url).mock(
        return_value=httpx.Response(200, content=truncated)
    )

    with pytest.raises(Unavailable, match="end-of-stream marker"):
        await _afetch(end_point, version, query, method)


@pytest.mark.parametrize("method", ["data", "stream_data"])
def test_corrupt_gzip_body(respx_mock, end_point, version, query, url, method):
    # The gzip magic number, followed by an unknown compression method
    corrupt = b"\x1f\x8b" + bytes(20)
    respx_mock.get(url).mock(return_value=httpx.Response(200, content=corrupt))

    with pytest.raises(Unavailable):
        _fetch(end_point, version, query, method)
