import time
import warnings

import httpx
import pytest

from pysdmx.api.qb import ApiVersion, LenientRestService, lenient

URL = "https://sdmx.example.org/data"


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
