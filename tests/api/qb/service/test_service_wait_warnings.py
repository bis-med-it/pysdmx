import asyncio
import time
import warnings

import httpx
import pytest

from pysdmx.api.qb import (
    ApiVersion,
    AsyncLenientRestService,
    DataContext,
    DataQuery,
    LenientRestService,
    lenient,
)

URL = "https://sdmx.example.org/data"
ENDPOINT = "https://sdmx.example.org"
QUERY = DataQuery(DataContext.DATAFLOW, "ESTAT", "UNE_RT_A", "1.0", "A.T")
QUERY_URL = "https://sdmx.example.org/data/dataflow/ESTAT/UNE_RT_A/1.0/A.T/"
WAITING = (
    f"Still waiting for {QUERY_URL} to start sending the message after "
    r"\d+ seconds \(timeout: 30 seconds\)"
)


@pytest.fixture
def service() -> LenientRestService:
    return LenientRestService(URL, ApiVersion.V2_0_0, timeout=30.0)


def slow_answer(request):
    time.sleep(0.4)
    return httpx.Response(200, content=b"<message/>")


def test_warns_while_waiting_for_the_message(respx_mock, service, monkeypatch):
    monkeypatch.setattr(lenient, "_WARN_AFTER", 0.05)
    monkeypatch.setattr(lenient, "_WARN_EVERY", 0.05)
    respx_mock.get(URL).mock(side_effect=slow_answer)

    with pytest.warns(
        UserWarning,
        match=(
            f"Still waiting for {URL} to start sending the message after "
            r"\d+ seconds \(timeout: 30 seconds\)"
        ),
    ) as warns:
        assert "".join(service.stream_message(URL)) == "<message/>"

    # One warning after the first wait, and more every wait afterwards
    assert len(warns) > 1


def test_does_not_warn_if_the_message_arrives_in_time(respx_mock, service):
    respx_mock.get(URL).mock(
        return_value=httpx.Response(200, content=b"<message/>")
    )

    with warnings.catch_warnings():
        warnings.simplefilter("error")
        assert "".join(service.stream_message(URL)) == "<message/>"


def read(service: LenientRestService, method: str) -> bytes:
    if method == "data":
        return service.data(QUERY)
    return b"".join(service.stream_data(QUERY))


async def aread(service: AsyncLenientRestService, method: str) -> bytes:
    if method == "data":
        return await service.data(QUERY)
    return b"".join([c async for c in service.stream_data(QUERY)])


@pytest.fixture
def slow_data(respx_mock, monkeypatch):
    monkeypatch.setattr(lenient, "_WARN_AFTER", 0.05)
    monkeypatch.setattr(lenient, "_WARN_EVERY", 0.05)
    respx_mock.get(QUERY_URL).mock(side_effect=slow_answer)


@pytest.mark.usefixtures("slow_data")
@pytest.mark.parametrize("method", ["data", "stream_data"])
def test_warns_while_waiting_for_the_data(method):
    service = LenientRestService(ENDPOINT, ApiVersion.V2_0_0, timeout=30.0)

    with pytest.warns(UserWarning, match=WAITING):
        data = read(service, method)

    assert data == b"<message/>"


@pytest.mark.asyncio
@pytest.mark.parametrize("method", ["data", "stream_data"])
async def test_async_warns_while_waiting_for_the_data(
    respx_mock, monkeypatch, method
):
    async def slow_async_answer(request):
        await asyncio.sleep(0.4)
        return httpx.Response(200, content=b"<message/>")

    monkeypatch.setattr(lenient, "_WARN_AFTER", 0.05)
    monkeypatch.setattr(lenient, "_WARN_EVERY", 0.05)
    respx_mock.get(QUERY_URL).mock(side_effect=slow_async_answer)
    service = AsyncLenientRestService(
        ENDPOINT, ApiVersion.V2_0_0, timeout=30.0
    )

    with pytest.warns(UserWarning, match=WAITING):
        data = await aread(service, method)

    assert data == b"<message/>"
