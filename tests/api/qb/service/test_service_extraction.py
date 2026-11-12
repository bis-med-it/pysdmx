import gzip
import re

import httpx
import pytest

from pysdmx.api.qb import ApiVersion, LenientRestService, lenient
from pysdmx.errors import InternalError, Invalid, NotImplemented, Unavailable
from tests.io.byte_chunks import ByteChunks, split

EXTRACTION = "423abd6b-c7b0-4530-b249-7216bf78c785"
URL = (
    "https://ec.europa.eu/eurostat/api/dissemination/sdmx/2.1/data/"
    "nrg_bal_c/A....DE"
)
ASYNC = "https://ec.europa.eu/eurostat/api/dissemination/1.0/async"
STATUS_URL = f"{ASYNC}/status/{EXTRACTION}"
DATA_URL = f"{ASYNC}/data/{EXTRACTION}"

# The answers of Eurostat's SDMX API: to a data query it queues as an
# asynchronous extraction, to the checks of the status of the extraction,
# and to the request of its data
QUEUED = (
    '<?xml version="1.0" encoding="UTF-8" ?>\n'
    '<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">'
    "<env:Header/><env:Body><ns0:syncResponse xmlns:ns0="
    '"http://estat.ec.europa.eu/disschain/soap/extraction">'
    "<processingTime>96</processingTime><queued>"
    f"<id>{EXTRACTION}</id><status>SUBMITTED</status>"
    "</queued></ns0:syncResponse></env:Body></env:Envelope>"
)
MESSAGE = (
    '<?xml version="1.0" encoding="UTF-8"?><m:GenericData xmlns:m="http://'
    'www.sdmx.org/resources/sdmxml/schemas/v2_1/message"/>'
)


def status_text(value: str) -> str:
    return (
        '<?xml version="1.0" encoding="UTF-8" ?>\n'
        '<env:Envelope xmlns:env="http://schemas.xmlsoap.org/soap/envelope/">'
        "<env:Header/><env:Body><ns0:asyncResponse xmlns:ns0="
        '"http://estat.ec.europa.eu/disschain/soap/asynchronous" xmlns:ns1='
        '"http://estat.ec.europa.eu/disschain/asynchronous"><ns1:status>'
        f"<ns1:key>{EXTRACTION}</ns1:key><ns1:status>{value}</ns1:status>"
        "</ns1:status></ns0:asyncResponse></env:Body></env:Envelope>"
    )


def body(text: str, compress: bool) -> bytes:
    # Eurostat may send gzip bodies without a Content-Encoding header
    return gzip.compress(text.encode()) if compress else text.encode()


def queued(compress: bool = False) -> httpx.Response:
    return httpx.Response(
        200,
        headers={
            "Content-Type": "application/xml",
            "Content-Disposition": f"attachment;filename={EXTRACTION}.xml",
        },
        content=body(QUEUED, compress),
    )


def status(value: str, compress: bool = False) -> httpx.Response:
    return httpx.Response(
        200,
        headers={
            "Content-Type": "application/xml",
            "Content-Disposition": f"attachment;filename={EXTRACTION}.xml",
        },
        content=body(status_text(value), compress),
    )


def data(compress: bool = False) -> httpx.Response:
    return httpx.Response(
        200,
        headers={
            "Content-Type": "application/octet-stream;charset=UTF-8",
            "Content-Disposition": (
                "attachment;filename=estat_nrg_bal_c_filtered.xml"
            ),
        },
        content=body(MESSAGE, compress),
    )


class Extraction:
    """An extraction, whose data can only be requested once available."""

    def __init__(self, *statuses: str, compress: bool = False):
        """Takes the statuses that the checks of the status answer."""
        self.__statuses = iter(statuses)
        self.__compress = compress
        self.__available = False

    def status(self, request: httpx.Request) -> httpx.Response:
        """Answers a check of the status with the next status."""
        value = next(self.__statuses)
        self.__available = value == "AVAILABLE"
        return status(value, self.__compress)

    def data(self, request: httpx.Request) -> httpx.Response:
        """Answers a request of the data, which must be available."""
        assert self.__available, "The data were requested before available"
        return data(self.__compress)


@pytest.fixture(autouse=True)
def no_wait(monkeypatch):
    monkeypatch.setattr(lenient, "_POLL_EVERY", 0.0)


@pytest.fixture
def service() -> LenientRestService:
    return LenientRestService(URL, ApiVersion.V2_0_0, timeout=30.0)


@pytest.mark.parametrize(
    ("url", "root"),
    [
        (URL, "https://ec.europa.eu/eurostat/api/dissemination"),
        (
            "https://ec.europa.eu/eurostat/api/dissemination/sdmx/3.0/data/"
            "dataflow/ESTAT/nrg_bal_c/1.0/*.*.*.*.DE?compress=false",
            "https://ec.europa.eu/eurostat/api/dissemination",
        ),
        (
            "https://ec.europa.eu/eurostat/api/comext/dissemination/sdmx/"
            "2.1/data/DS-045409/M.EU.DE.1.1",
            "https://ec.europa.eu/eurostat/api/comext/dissemination",
        ),
    ],
)
@pytest.mark.parametrize("timeout", [30.0, None])
def test_streams_the_data_of_a_queued_extraction(
    respx_mock, url, root, timeout
):
    extraction = Extraction("PROCESSING", "AVAILABLE")
    respx_mock.get(url).mock(return_value=queued())
    respx_mock.get(f"{root}/1.0/async/status/{EXTRACTION}").mock(
        side_effect=extraction.status
    )
    respx_mock.get(f"{root}/1.0/async/data/{EXTRACTION}").mock(
        side_effect=extraction.data
    )
    service = LenientRestService(url, ApiVersion.V2_0_0, timeout=timeout)

    assert "".join(service.stream_message(url)) == MESSAGE


def test_follows_an_extraction_queued_in_small_chunks(respx_mock, service):
    extraction = Extraction("AVAILABLE")
    respx_mock.get(URL).mock(
        return_value=httpx.Response(
            200, stream=ByteChunks(split(QUEUED.encode(), 50))
        )
    )
    respx_mock.get(STATUS_URL).mock(side_effect=extraction.status)
    respx_mock.get(DATA_URL).mock(side_effect=extraction.data)

    assert "".join(service.stream_message(URL)) == MESSAGE


def test_decompresses_the_answers_of_an_extraction(respx_mock, service):
    extraction = Extraction("PROCESSING", "AVAILABLE", compress=True)
    respx_mock.get(URL).mock(return_value=queued(compress=True))
    respx_mock.get(STATUS_URL).mock(side_effect=extraction.status)
    respx_mock.get(DATA_URL).mock(side_effect=extraction.data)

    assert "".join(service.stream_message(URL)) == MESSAGE


def test_raises_if_the_extraction_is_not_available_in_time(
    respx_mock, monkeypatch
):
    monkeypatch.setattr(lenient, "_POLL_EVERY", 0.05)
    respx_mock.get(URL).mock(return_value=queued())
    # Limited checks, so that the test ends if the timeout is ignored
    respx_mock.get(STATUS_URL).mock(
        side_effect=[status("PROCESSING") for _ in range(100)]
    )
    service = LenientRestService(URL, ApiVersion.V2_0_0, timeout=0.2)

    with pytest.raises(Unavailable) as error:
        "".join(service.stream_message(URL))

    assert EXTRACTION in str(error.value)
    assert "0.2 seconds" in str(error.value)
    assert DATA_URL in str(error.value)


@pytest.mark.parametrize("value", ["EXPIRED", "ERROR"])
def test_raises_if_the_extraction_fails(respx_mock, service, value):
    respx_mock.get(URL).mock(return_value=queued())
    respx_mock.get(STATUS_URL).mock(
        side_effect=[status("PROCESSING"), status(value)]
    )

    with pytest.raises(Unavailable, match=value) as error:
        "".join(service.stream_message(URL))

    assert EXTRACTION in str(error.value)
    assert STATUS_URL in str(error.value)


def test_raises_the_error_of_a_status_check(respx_mock, service):
    respx_mock.get(URL).mock(return_value=queued())
    # Eurostat's answer for an extraction it does not know
    respx_mock.get(STATUS_URL).mock(
        return_value=httpx.Response(
            400,
            headers={"Content-Type": "application/xml"},
            content=(
                '<?xml version="1.0" encoding="UTF-8"?><S:Fault xmlns:S='
                '"http://schemas.xmlsoap.org/soap/envelope/"><faultcode>100'
                "</faultcode><faultstring>UNKNOWN_REQUEST: Unknown request."
                "</faultstring></S:Fault>"
            ),
        )
    )

    with pytest.raises(Invalid, match="UNKNOWN_REQUEST: Unknown request."):
        "".join(service.stream_message(URL))


def test_raises_if_the_status_is_missing(respx_mock, service):
    respx_mock.get(URL).mock(return_value=queued())
    respx_mock.get(STATUS_URL).mock(
        return_value=httpx.Response(
            200, content="<html><body>Under maintenance</body></html>"
        )
    )

    with pytest.raises(InternalError, match="Under maintenance") as error:
        "".join(service.stream_message(URL))

    assert EXTRACTION in str(error.value)


def test_raises_the_error_of_the_data_request(respx_mock, service):
    respx_mock.get(URL).mock(return_value=queued())
    respx_mock.get(STATUS_URL).mock(return_value=status("AVAILABLE"))
    # The XML body of the error is not streamed as the message, as an
    # SDMX-ML error message answering the query would be: it is not one
    respx_mock.get(DATA_URL).mock(
        return_value=httpx.Response(
            500,
            headers={"Content-Type": "application/xml"},
            content=(
                '<?xml version="1.0" encoding="UTF-8"?><S:Fault xmlns:S='
                '"http://schemas.xmlsoap.org/soap/envelope/"><faultcode>'
                "SERVER</faultcode><faultstring>null</faultstring></S:Fault>"
            ),
        )
    )

    with pytest.raises(InternalError, match="SERVER"):
        "".join(service.stream_message(URL))


def test_streams_a_soap_message_that_queues_no_extraction(respx_mock, service):
    respx_mock.get(URL).mock(return_value=status("AVAILABLE"))

    assert "".join(service.stream_message(URL)) == status_text("AVAILABLE")


def test_raises_if_the_extraction_urls_are_unknown(respx_mock):
    url = "https://sdmx.example.org/data/nrg_bal_c/A....DE"
    respx_mock.get(url).mock(return_value=queued())
    service = LenientRestService(url, ApiVersion.V2_0_0)

    with pytest.raises(NotImplemented, match=EXTRACTION):
        "".join(service.stream_message(url))


def test_warns_while_waiting_for_the_extraction(
    respx_mock, service, monkeypatch
):
    monkeypatch.setattr(lenient, "_WARN_AFTER", 0.0)
    monkeypatch.setattr(lenient, "_WARN_EVERY", 0.01)
    monkeypatch.setattr(lenient, "_POLL_EVERY", 0.2)
    extraction = Extraction("PROCESSING", "AVAILABLE")
    respx_mock.get(URL).mock(return_value=queued())
    respx_mock.get(STATUS_URL).mock(side_effect=extraction.status)
    respx_mock.get(DATA_URL).mock(side_effect=extraction.data)

    with pytest.warns(UserWarning, match="Still waiting for") as record:
        assert "".join(service.stream_message(URL)) == MESSAGE

    # The first warnings may come before the extraction is queued
    waiting = re.compile(
        f"Still waiting for the asynchronous extraction {EXTRACTION} of "
        rf"{re.escape(URL)} after \d+ seconds \(timeout: 30 seconds\)"
    )
    assert any(waiting.fullmatch(str(w.message)) for w in record)
