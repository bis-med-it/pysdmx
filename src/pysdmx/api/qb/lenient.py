"""Lenient connectors to SDMX-REST services."""

import codecs
import contextlib
import itertools
import re
import threading
import time
import warnings
from typing import (
    AsyncGenerator,
    AsyncIterable,
    Generator,
    Iterable,
    Iterator,
    List,
    Optional,
    Tuple,
)

import httpx

from pysdmx import errors
from pysdmx.api.qb.service import AsyncRestService, RestService
from pysdmx.util._net_utils import (
    adecompress_gzip,
    decompress_gzip,
    map_httpx_errors,
)

# The seconds without an answer after which a warning is emitted, and the
# seconds between that warning and the next ones
_WARN_AFTER = 60.0
_WARN_EVERY = 10.0

# When a data query is too large to be answered at once, Eurostat's SDMX
# API queues it as an asynchronous extraction: instead of the data, it
# answers with a SOAP message that holds the id of the extraction. Other
# SOAP messages, from a URL of their own, tell the status of the extraction,
# and its data are sent from a third URL once it is available.
_SOAP = re.compile(r"\s*(?:<\?xml[^>]*\?>\s*)?<(?:[\w.-]+:)?Envelope[\s/>]")
_QUEUED = re.compile(
    r"<(?:[\w.-]+:)?queued>\s*<(?:[\w.-]+:)?id>\s*([\w-]+)\s*</"
)
_STATUS = re.compile(r"<(?:[\w.-]+:)?status>\s*(\w+)\s*</")
# The characters at the start of a message that tell if it is a SOAP
# message, and those of a SOAP message in which the id of the extraction it
# may queue is looked for
_SOAP_HEAD = 256
_SOAP_MAX = 65536
# The seconds between two checks of the status of an extraction
_POLL_EVERY = 10.0
# The statuses of an extraction that is not available yet
_WAITING = ("SUBMITTED", "PROCESSING")


def _still_waiting(what: str, start: float, timeout: Optional[float]) -> str:
    """Builds the message of a warning about a long wait."""
    elapsed = round(time.monotonic() - start)
    limit = "" if timeout is None else f" (timeout: {timeout:g} seconds)"
    return f"{what} after {elapsed} seconds{limit}"


class _WaitWarnings:
    """Warns, while a block runs, that the service is taking long to answer.

    The block is blocked itself, so the warnings are emitted from a thread.

    Attributes:
        what: What the block waits for, as the warnings tell it.
        start: When the wait started, as a ``time.monotonic()`` value.
    """

    def __init__(self, url: str, timeout: Optional[float]) -> None:
        self.what = f"Still waiting for {url} to start sending the message"
        self.start = time.monotonic()
        self.__timeout = timeout
        self.__done = threading.Event()
        self.__thread = threading.Thread(target=self.__warn, daemon=True)

    def __enter__(self) -> "_WaitWarnings":
        self.__thread.start()
        return self

    def __exit__(self, *args: object) -> None:
        self.__done.set()
        self.__thread.join()

    def __warn(self) -> None:
        wait = _WARN_AFTER
        while not self.__done.wait(wait):
            warnings.warn(
                _still_waiting(self.what, self.start, self.__timeout),
                UserWarning,
                stacklevel=1,
            )
            wait = _WARN_EVERY


def _read(chunks: Iterator[str], size: int) -> List[str]:
    """Reads the next chunks of a text, until they hold size characters."""
    read = []
    length = 0
    for chunk in chunks:
        read.append(chunk)
        length += len(chunk)
        if length >= size:
            break
    return read


def _queued_extraction(
    chunks: Iterator[str],
) -> Tuple[List[str], Optional[str]]:
    """Reads the start of a message, to know if it queues an extraction.

    The message queues an extraction if it is a SOAP message that holds the
    id of the extraction. A SOAP message is small, so it is read whole (up
    to _SOAP_MAX characters); only the start of any other message is read.

    Returns:
        The chunks read, and the id of the extraction, if one is queued.
    """
    head = _read(chunks, _SOAP_HEAD)
    if not _SOAP.match("".join(head)):
        return head, None
    head += _read(chunks, _SOAP_MAX)
    queued = _QUEUED.search("".join(head))
    return head, queued.group(1) if queued else None


def _extraction_status(text: str, extraction: str, url: str) -> str:
    """Returns the status of an extraction, from a message that tells it."""
    status = _STATUS.search(text)
    if status is None:
        raise errors.InternalError(
            "Unexpected answer",
            f"The status of the asynchronous extraction {extraction} is not "
            f"found in the answer from {url}: {text[:500]}",
        )
    return status.group(1)


class _Extraction:
    """An asynchronous extraction of Eurostat's SDMX API.

    Attributes:
        id: The id of the extraction.
        status_url: The URL that tells the status of the extraction.
        data_url: The URL of the data, once the extraction is available.
    """

    def __init__(self, extraction: str, url: httpx.URL) -> None:
        # The URLs are in the API whose base is the path before /sdmx/
        base, sdmx, _ = url.path.partition("/sdmx/")
        if not sdmx:
            raise errors.NotImplemented(
                "Unsupported extraction",
                f"The service queued {url} as the asynchronous extraction "
                f"{extraction}, but how to follow it is only known for "
                "Eurostat's SDMX APIs.",
            )

        def url_of(kind: str) -> str:
            path = f"{base}/1.0/async/{kind}/{extraction}"
            return str(url.copy_with(path=path, query=None, fragment=None))

        self.id = extraction
        self.status_url = url_of("status")
        self.data_url = url_of("data")


class LenientRestService(RestService):
    """A lenient synchronous connector to SDMX-REST services.

    It is instantiated and used as the
    :class:`~pysdmx.api.qb.RestService`, which is strict: it expects the
    service to be protocol-correct. This connector also accepts the
    following deviations:

    * A response body compressed with gzip, but sent without a
      ``Content-Encoding`` header (e.g. by Eurostat's SDMX API), is
      decompressed if its first bytes are those of a gzip stream.
    * A data query that Eurostat's SDMX API queues as an asynchronous
      extraction, answering with the id of the extraction instead of the
      data, is followed by :meth:`stream_message`, which streams the data
      once the extraction is available.
    """

    def stream_message(self, url: str) -> Generator[str, None, None]:
        """Streams the text of the SDMX message found at a URL.

        The URL is requested as it is, whatever the endpoint of the service
        is. If the service answers with an error status and an XML body, as
        an SDMX-ML error message, the body is streamed as the message, so
        that the error it describes can be read.

        If the service queues the query as an asynchronous extraction, as
        Eurostat's SDMX API does with large data queries, the status of the
        extraction is checked every 10 seconds, until it is available or
        the timeout of the connector has passed since the request, and the
        data of the extraction are streamed as the message.

        If the service has not started to send the message after 60
        seconds, a ``UserWarning`` is emitted, and another one every 10
        seconds while it keeps waiting.

        Args:
            url: The URL of the message.

        Yields:
            The chunks of the text of the message, decoded with the charset
            declared by the service (UTF-8 by default).

        Raises:
            NotFound: If the message is not found.
            Invalid: If the service answers with another client error.
            InternalError: If the service answers with a server error, or
                does not tell the status of an extraction.
            Unavailable: If the service cannot be reached, the response
                cannot be decoded, or an extraction fails or is not
                available in time.
            NotImplemented: If the service queues the query as an extraction
                that cannot be followed, outside Eurostat's SDMX APIs.
        """
        with httpx.Client(
            verify=self._ssl_context, follow_redirects=True
        ) as client:
            try:
                with contextlib.ExitStack() as stack:
                    with _WaitWarnings(url, self._timeout) as wait:
                        chunks = self.__open(client, stack, url, wait)
                    yield from chunks
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)

    def __open(
        self,
        client: httpx.Client,
        stack: contextlib.ExitStack,
        url: str,
        wait: _WaitWarnings,
    ) -> Iterator[str]:
        """Requests the message, following the extraction it is queued as."""
        response = self.__get(client, stack, url)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            # The body of an error is read whole: it is small, and
            # map_httpx_errors needs it
            response.read()
            if "<?xml" in response.text:
                return iter((response.text,))
            raise
        chunks = self.__text(response)
        head, extraction_id = _queued_extraction(chunks)
        if extraction_id is None:
            return itertools.chain(head, chunks)
        response.close()
        extraction = _Extraction(extraction_id, response.url)
        wait.what = (
            f"Still waiting for the asynchronous extraction {extraction_id} "
            f"of {url}"
        )
        status = _extraction_status("".join(head), extraction_id, url)
        self.__wait_for(client, extraction, status, wait.start)
        response = self.__get(client, stack, extraction.data_url)
        if response.is_error:
            # The error is not an SDMX-ML error message answering the query
            response.read()
            response.raise_for_status()
        return self.__text(response)

    def __wait_for(
        self,
        client: httpx.Client,
        extraction: _Extraction,
        status: str,
        start: float,
    ) -> None:
        """Waits for an extraction to be available."""
        timeout = self._timeout
        while status in _WAITING:
            pause = _POLL_EVERY
            if timeout is not None:
                left = start + timeout - time.monotonic()
                if left <= 0:
                    raise errors.Unavailable(
                        "Extraction not available",
                        "The service queued the query as the asynchronous "
                        f"extraction {extraction.id}, which was not "
                        f"available after {timeout:g} seconds. Its data can "
                        f"be read from {extraction.data_url} once its "
                        f"status, at {extraction.status_url}, is AVAILABLE.",
                    )
                pause = min(pause, left)
            time.sleep(pause)
            response = client.get(
                extraction.status_url,
                headers=self._headers,
                timeout=self._timeout,
            )
            response.raise_for_status()
            text = b"".join(
                self._decode([response.content], response.request)
            ).decode(response.encoding or "utf-8", errors="replace")
            status = _extraction_status(
                text, extraction.id, extraction.status_url
            )
        if status != "AVAILABLE":
            raise errors.Unavailable(
                "Extraction not available",
                "The service queued the query as the asynchronous extraction "
                f"{extraction.id}, whose status is {status} at "
                f"{extraction.status_url}.",
            )

    def __get(
        self,
        client: httpx.Client,
        stack: contextlib.ExitStack,
        url: str,
    ) -> httpx.Response:
        """Requests a URL; the response is closed as the stack is."""
        return stack.enter_context(
            client.stream(
                "GET", url, headers=self._headers, timeout=self._timeout
            )
        )

    def __text(self, response: httpx.Response) -> Iterator[str]:
        """Returns the chunks of the text of the body of a response."""
        return codecs.iterdecode(
            self._decode(response.iter_bytes(), response.request),
            response.encoding or "utf-8",
            errors="replace",
        )

    def _decode(
        self, chunks: Iterable[bytes], request: httpx.Request
    ) -> Generator[bytes, None, None]:
        # httpx decodes the body from its Content-Encoding, but some
        # services (e.g. Eurostat) send a gzip body without one
        return decompress_gzip(chunks, request)


class AsyncLenientRestService(AsyncRestService):
    """A lenient asynchronous connector to SDMX-REST services.

    It is instantiated and used as the
    :class:`~pysdmx.api.qb.AsyncRestService`, which is strict, but, as the
    :class:`~pysdmx.api.qb.LenientRestService`, it also decompresses a
    response body compressed with gzip but sent without a
    ``Content-Encoding`` header.
    """

    def _decode(
        self, chunks: Iterable[bytes], request: httpx.Request
    ) -> Generator[bytes, None, None]:
        return decompress_gzip(chunks, request)

    def _adecode(
        self, chunks: AsyncIterable[bytes], request: httpx.Request
    ) -> AsyncGenerator[bytes, None]:
        return adecompress_gzip(chunks, request)
