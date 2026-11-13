"""Lenient connectors to SDMX-REST services."""

import asyncio
import codecs
import contextlib
import itertools
import re
import threading
import time
import warnings
from typing import (
    AsyncGenerator,
    AsyncIterator,
    Generator,
    Iterator,
    List,
    Optional,
    Tuple,
)

import httpx

from pysdmx import errors
from pysdmx.api.qb.availability import AvailabilityFormat
from pysdmx.api.qb.data import DataFormat, DataQuery
from pysdmx.api.qb.refmeta import RefMetaFormat
from pysdmx.api.qb.registration import RegistryFormat
from pysdmx.api.qb.schema import SchemaFormat
from pysdmx.api.qb.service import (
    AsyncRestService,
    RestService,
    _add_query_slash,
    _sanitize_query,
)
from pysdmx.api.qb.structure import StructureFormat
from pysdmx.api.qb.util import ApiVersion
from pysdmx.util._net_utils import (
    adecompress_gzip,
    decompress_gzip,
    map_httpx_errors,
)

# The seconds without an answer after which a warning is emitted, and the
# seconds between that warning and the next ones
_WARN_AFTER = 60.0
_WARN_EVERY = 10.0

# Eurostat's SDMX API sends SOAP messages, besides SDMX ones. Instead of an
# SDMX-ML error message, it describes an error in a SOAP fault, without an
# envelope. When a data query is too large to be answered at once, it
# queues it as an asynchronous extraction: instead of the data, it answers
# with a SOAP message that holds the id of the extraction. Other SOAP
# messages, from a URL of their own, tell the status of the extraction, and
# its data are sent from a third URL once it is available.
_SOAP = re.compile(
    r"\s*(?:<\?xml[^>]*\?>\s*)?<(?:[\w.-]+:)?(?:Envelope|Fault)[\s/>]"
)
_QUEUED = re.compile(
    r"<(?:[\w.-]+:)?queued>\s*<(?:[\w.-]+:)?id>\s*([\w-]+)\s*</"
)
_STATUS = re.compile(r"<(?:[\w.-]+:)?status>\s*(\w+)\s*</")
# The bytes at the start of a body that tell if it is a SOAP message, and
# those of a SOAP message in which the id of the extraction it may queue is
# looked for
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


class _Wait:
    """A wait for a service to start sending a message.

    The subclasses warn about it while it takes long.

    Attributes:
        start: When the wait started, as a ``time.monotonic()`` value.
    """

    def __init__(self, url: str, timeout: Optional[float]) -> None:
        self.start = time.monotonic()
        self.__url = url
        self.__what = f"Still waiting for {url} to start sending the message"
        self.__timeout = timeout

    def queued(self, extraction: str, timeout: Optional[float]) -> None:
        """Tells that the message is the data of a queued extraction."""
        self.__what = (
            f"Still waiting for the asynchronous extraction {extraction} of "
            f"{self.__url}"
        )
        self.__timeout = timeout

    def _warn(self) -> None:
        warnings.warn(
            _still_waiting(self.__what, self.start, self.__timeout),
            UserWarning,
            stacklevel=1,
        )


class _WaitWarnings(_Wait):
    """Warns, while a block runs, that the service is taking long to answer.

    The block is blocked itself, so the warnings are emitted from a thread.
    """

    def __init__(self, url: str, timeout: Optional[float]) -> None:
        super().__init__(url, timeout)
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
            self._warn()
            wait = _WARN_EVERY


class _AsyncWaitWarnings(_Wait):
    """Warns, while an asynchronous block runs, that it is taking long.

    The warnings are emitted from a task.
    """

    async def __aenter__(self) -> "_AsyncWaitWarnings":
        self.__task = asyncio.create_task(self.__warn())
        return self

    async def __aexit__(self, *args: object) -> None:
        self.__task.cancel()
        await asyncio.wait({self.__task})

    async def __warn(self) -> None:
        wait = _WARN_AFTER
        while True:
            await asyncio.sleep(wait)
            self._warn()
            wait = _WARN_EVERY


def _read(chunks: Iterator[bytes], size: int) -> List[bytes]:
    """Reads the next chunks of a body, until they hold size bytes."""
    read = []
    length = 0
    for chunk in chunks:
        read.append(chunk)
        length += len(chunk)
        if length >= size:
            break
    return read


async def _aread(chunks: AsyncIterator[bytes], size: int) -> List[bytes]:
    """Reads the next chunks of a body, until they hold size bytes."""
    read = []
    length = 0
    async for chunk in chunks:
        read.append(chunk)
        length += len(chunk)
        if length >= size:
            break
    return read


async def _achain(
    head: List[bytes], chunks: AsyncIterator[bytes]
) -> AsyncGenerator[bytes, None]:
    """Yields the chunks of a body already read, and then the rest."""
    for chunk in head:
        yield chunk
    async for chunk in chunks:
        yield chunk


def _text(chunks: List[bytes]) -> str:
    """Decodes the chunks of a body, to look for SOAP messages in it."""
    return b"".join(chunks).decode("utf-8", errors="replace")


def _queued_id(text: str) -> Optional[str]:
    """Returns the id of the extraction that a SOAP message queues, if any."""
    queued = _QUEUED.search(text)
    return queued.group(1) if queued else None


def _queued_extraction(
    chunks: Iterator[bytes],
) -> Tuple[List[bytes], Optional[str]]:
    """Reads the start of a body, to know if it queues an extraction.

    The body queues an extraction if it is a SOAP message that holds the id
    of the extraction. A SOAP message is small, so it is read whole (up to
    _SOAP_MAX bytes); only the start of any other body is read.

    Returns:
        The chunks read, and the id of the extraction, if one is queued.
    """
    head = _read(chunks, _SOAP_HEAD)
    if not _SOAP.match(_text(head)):
        return head, None
    head += _read(chunks, _SOAP_MAX)
    return head, _queued_id(_text(head))


async def _aqueued_extraction(
    chunks: AsyncIterator[bytes],
) -> Tuple[List[bytes], Optional[str]]:
    """Reads the start of a body, as _queued_extraction does."""
    head = await _aread(chunks, _SOAP_HEAD)
    if not _SOAP.match(_text(head)):
        return head, None
    head += await _aread(chunks, _SOAP_MAX)
    return head, _queued_id(_text(head))


def _raise_for_status(response: httpx.Response) -> None:
    """Raises the error of a streamed response, read for map_httpx_errors."""
    if response.is_error:
        response.read()
        response.raise_for_status()


async def _araise_for_status(response: httpx.Response) -> None:
    """Raises the error of a streamed response, as _raise_for_status does."""
    if response.is_error:
        await response.aread()
        response.raise_for_status()


def _body_text(response: httpx.Response) -> str:
    """Returns the text of the body of a response that is read whole."""
    body = b"".join(decompress_gzip([response.content], response.request))
    return body.decode(response.encoding or "utf-8", errors="replace")


def _url(endpoint: str, query: str) -> str:
    """Returns the URL of a query, as the REST services build it."""
    return f"{endpoint}{_sanitize_query(_add_query_slash(query))}"


class _Extraction:
    """An asynchronous extraction of Eurostat's SDMX API.

    Its status is checked until it is available, or until the timeout has
    passed since the start of the wait.

    Attributes:
        id: The id of the extraction.
        status_url: The URL that tells the status of the extraction.
        data_url: The URL of the data, once the extraction is available.
    """

    def __init__(
        self,
        extraction: str,
        url: httpx.URL,
        timeout: Optional[float],
        start: float,
    ) -> None:
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
        self.__timeout = timeout
        self.__start = start

    def status(self, text: str, url: str) -> str:
        """Returns the status of the extraction, from a message that tells it.

        Raises:
            InternalError: If the message does not tell it.
        """
        status = _STATUS.search(text)
        if status is None:
            raise errors.InternalError(
                "Unexpected answer",
                f"The status of the asynchronous extraction {self.id} is not "
                f"found in the answer from {url}: {text[:500]}",
            )
        return status.group(1)

    def available(self, status: str) -> bool:
        """Tells if the extraction is available, from its status.

        Raises:
            Unavailable: If the extraction failed.
        """
        if status in _WAITING:
            return False
        if status != "AVAILABLE":
            raise errors.Unavailable(
                "Extraction not available",
                "The service queued the query as the asynchronous extraction "
                f"{self.id}, whose status is {status} at {self.status_url}.",
            )
        return True

    def pause(self) -> float:
        """Returns the seconds to wait before checking the status again.

        Raises:
            Unavailable: If the timeout has passed.
        """
        if self.__timeout is None:
            return _POLL_EVERY
        left = self.__start + self.__timeout - time.monotonic()
        if left <= 0:
            raise errors.Unavailable(
                "Extraction not available",
                "The service queued the query as the asynchronous extraction "
                f"{self.id}, which was not available after "
                f"{self.__timeout:g} seconds. Its data can be read from "
                f"{self.data_url} once its status, at {self.status_url}, is "
                "AVAILABLE.",
            )
        return min(_POLL_EVERY, left)


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
      data, is followed: :meth:`data`, :meth:`stream_data` and
      :meth:`stream_message` return the data of the extraction once it is
      available.
    * An error that Eurostat's SDMX API describes in a SOAP fault, instead
      of an SDMX-ML error message, is raised by :meth:`stream_message` as
      any other error, with the fault in its message.

    Besides the arguments of the :class:`~pysdmx.api.qb.RestService`, it
    takes the following one.

    Args:
        extraction_timeout: The maximum number of seconds to wait, since
            the query, for an asynchronous extraction to be available, or
            ``None`` to wait without limit. Defaults to 600 seconds.
    """

    def __init__(
        self,
        api_endpoint: str,
        api_version: ApiVersion,
        data_format: DataFormat = DataFormat.SDMX_JSON_2_0_0,
        structure_format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        schema_format: SchemaFormat = SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE,
        refmeta_format: RefMetaFormat = RefMetaFormat.SDMX_JSON_2_0_0,
        avail_format: AvailabilityFormat = AvailabilityFormat.SDMX_JSON_2_0_0,
        registry_format: RegistryFormat = RegistryFormat.FUSION_JSON,
        pem: Optional[str] = None,
        timeout: Optional[float] = 5.0,
        extraction_timeout: Optional[float] = 600.0,
    ):
        """Instantiate a lenient connector to a SDMX-REST service."""
        super().__init__(
            api_endpoint,
            api_version,
            data_format,
            structure_format,
            schema_format,
            refmeta_format,
            avail_format,
            registry_format,
            pem,
            timeout,
        )
        self._extraction_timeout = extraction_timeout

    def data(self, query: DataQuery) -> bytes:
        """Execute a data query against the service.

        An asynchronous extraction is followed, and a long wait warned
        about, as by :meth:`stream_data`.
        """
        return b"".join(self.stream_data(query))

    def stream_data(
        self, query: DataQuery, chunk_size: int = 8192
    ) -> Generator[bytes, None, None]:
        """Execute a data query against the service.

        If the service queues the query as an asynchronous extraction, as
        Eurostat's SDMX API does with large data queries, the status of the
        extraction is checked every 10 seconds, until it is available or
        ``extraction_timeout`` seconds have passed since the query, and the
        data of the extraction are streamed.

        If the service has not started to send the data after 60 seconds, a
        ``UserWarning`` is emitted, and another one every 10 seconds while
        it keeps waiting.
        """
        url = _url(self._api_endpoint, query.get_url(self._api_version, True))
        headers = {**self._headers, "Accept": self._data_format.value}
        with self.__client() as client:
            try:
                with contextlib.ExitStack() as stack:
                    with _WaitWarnings(url, self._timeout) as wait:
                        response = self.__get(client, stack, url, headers)
                        _raise_for_status(response)
                        chunks, _ = self.__body(
                            client, stack, response, wait, chunk_size
                        )
                    yield from chunks
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)

    def stream_message(self, url: str) -> Generator[str, None, None]:
        """Streams the text of the SDMX message found at a URL.

        The URL is requested as it is, whatever the endpoint of the service
        is. If the service answers with an error status and an XML body, as
        an SDMX-ML error message, the body is streamed as the message, so
        that the error it describes can be read. A SOAP fault, in which
        Eurostat's SDMX API describes its errors instead, is raised as any
        other error.

        If the service queues the query as an asynchronous extraction, as
        Eurostat's SDMX API does with large data queries, the status of the
        extraction is checked every 10 seconds, until it is available or
        ``extraction_timeout`` seconds have passed since the request, and
        the data of the extraction are streamed as the message.

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
        with self.__client() as client:
            try:
                with contextlib.ExitStack() as stack:
                    with _WaitWarnings(url, self._timeout) as wait:
                        text = self.__message(client, stack, url, wait)
                    yield from text
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)

    def __message(
        self,
        client: httpx.Client,
        stack: contextlib.ExitStack,
        url: str,
        wait: _Wait,
    ) -> Iterator[str]:
        """Requests a message, and returns the chunks of its text."""
        response = self.__get(client, stack, url, self._headers)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError:
            # The body of an error is read whole: it is small, and
            # map_httpx_errors needs it. An SDMX-ML error message is
            # streamed as the message, but not a SOAP fault.
            response.read()
            if "<?xml" in response.text and not _SOAP.match(response.text):
                return iter((response.text,))
            raise
        chunks, response = self.__body(client, stack, response, wait, None)
        return codecs.iterdecode(
            chunks, response.encoding or "utf-8", errors="replace"
        )

    def __body(
        self,
        client: httpx.Client,
        stack: contextlib.ExitStack,
        response: httpx.Response,
        wait: _Wait,
        chunk_size: Optional[int],
    ) -> Tuple[Iterator[bytes], httpx.Response]:
        """Returns the chunks of the body of a response.

        If the response queues an extraction, the chunks of the data of the
        extraction are returned instead, once it is available. The response
        that the chunks come from is returned too.
        """
        chunks = decompress_gzip(
            response.iter_bytes(chunk_size), response.request
        )
        head, extraction_id = _queued_extraction(chunks)
        if extraction_id is None:
            return itertools.chain(head, chunks), response
        response.close()
        extraction = _Extraction(
            extraction_id, response.url, self._extraction_timeout, wait.start
        )
        wait.queued(extraction_id, self._extraction_timeout)
        status = extraction.status(_text(head), str(response.url))
        while not extraction.available(status):
            time.sleep(extraction.pause())
            status = self.__status(client, extraction)
        response = self.__get(
            client, stack, extraction.data_url, self._headers
        )
        _raise_for_status(response)
        return (
            decompress_gzip(response.iter_bytes(chunk_size), response.request),
            response,
        )

    def __status(self, client: httpx.Client, extraction: _Extraction) -> str:
        """Checks the status of an extraction."""
        response = client.get(
            extraction.status_url, headers=self._headers, timeout=self._timeout
        )
        response.raise_for_status()
        text = _body_text(response)
        return extraction.status(text, extraction.status_url)

    def __client(self) -> httpx.Client:
        return httpx.Client(verify=self._ssl_context, follow_redirects=True)

    def __get(
        self,
        client: httpx.Client,
        stack: contextlib.ExitStack,
        url: str,
        headers: dict[str, str],
    ) -> httpx.Response:
        """Requests a URL; the response is closed as the stack is."""
        return stack.enter_context(
            client.stream("GET", url, headers=headers, timeout=self._timeout)
        )

    def _fetch(self, query: str, format: str) -> bytes:
        # httpx decodes the body from its Content-Encoding, but some
        # services (e.g. Eurostat) send a gzip body without one
        headers = {**self._headers, "Accept": format}
        with self.__client() as client:
            try:
                response = client.get(
                    _url(self._api_endpoint, query),
                    headers=headers,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                return b"".join(
                    decompress_gzip([response.content], response.request)
                )
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)


class AsyncLenientRestService(AsyncRestService):
    """A lenient asynchronous connector to SDMX-REST services.

    It is instantiated and used as the
    :class:`~pysdmx.api.qb.AsyncRestService`, which is strict, but, as the
    :class:`~pysdmx.api.qb.LenientRestService`, it also decompresses a
    response body compressed with gzip but sent without a
    ``Content-Encoding`` header, and :meth:`data` and :meth:`stream_data`
    follow the asynchronous extractions in which Eurostat's SDMX API queues
    large data queries.

    Besides the arguments of the :class:`~pysdmx.api.qb.AsyncRestService`,
    it takes the following one.

    Args:
        extraction_timeout: The maximum number of seconds to wait, since
            the query, for an asynchronous extraction to be available, or
            ``None`` to wait without limit. Defaults to 600 seconds.
    """

    def __init__(
        self,
        api_endpoint: str,
        api_version: ApiVersion,
        data_format: DataFormat = DataFormat.SDMX_JSON_2_0_0,
        structure_format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        schema_format: SchemaFormat = SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE,
        refmeta_format: RefMetaFormat = RefMetaFormat.SDMX_JSON_2_0_0,
        avail_format: AvailabilityFormat = AvailabilityFormat.SDMX_JSON_2_0_0,
        registry_format: RegistryFormat = RegistryFormat.FUSION_JSON,
        pem: Optional[str] = None,
        timeout: Optional[float] = 5.0,
        extraction_timeout: Optional[float] = 600.0,
    ):
        """Instantiate a lenient connector to a SDMX-REST service."""
        super().__init__(
            api_endpoint,
            api_version,
            data_format,
            structure_format,
            schema_format,
            refmeta_format,
            avail_format,
            registry_format,
            pem,
            timeout,
        )
        self._extraction_timeout = extraction_timeout

    async def data(self, query: DataQuery) -> bytes:
        """Execute a data query against the service.

        An asynchronous extraction is followed, and a long wait warned
        about, as by :meth:`stream_data`.
        """
        return b"".join([chunk async for chunk in self.stream_data(query)])

    async def stream_data(
        self, query: DataQuery, chunk_size: int = 8192
    ) -> AsyncGenerator[bytes, None]:
        """Execute a data query against the service.

        If the service queues the query as an asynchronous extraction, as
        Eurostat's SDMX API does with large data queries, the status of the
        extraction is checked every 10 seconds, until it is available or
        ``extraction_timeout`` seconds have passed since the query, and the
        data of the extraction are streamed.

        If the service has not started to send the data after 60 seconds, a
        ``UserWarning`` is emitted, and another one every 10 seconds while
        it keeps waiting.
        """
        url = _url(self._api_endpoint, query.get_url(self._api_version, True))
        headers = {**self._headers, "Accept": self._data_format.value}
        async with httpx.AsyncClient(
            verify=self._ssl_context, follow_redirects=True
        ) as client:
            try:
                async with contextlib.AsyncExitStack() as stack:
                    async with _AsyncWaitWarnings(url, self._timeout) as wait:
                        response = await self.__get(
                            client, stack, url, headers
                        )
                        await _araise_for_status(response)
                        chunks = await self.__body(
                            client, stack, response, wait, chunk_size
                        )
                    async for chunk in chunks:
                        yield chunk
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)

    async def __body(
        self,
        client: httpx.AsyncClient,
        stack: contextlib.AsyncExitStack,
        response: httpx.Response,
        wait: _Wait,
        chunk_size: int,
    ) -> AsyncIterator[bytes]:
        """Returns the chunks of the body of a response.

        If the response queues an extraction, the chunks of the data of the
        extraction are returned instead, once it is available.
        """
        chunks = adecompress_gzip(
            response.aiter_bytes(chunk_size), response.request
        )
        head, extraction_id = await _aqueued_extraction(chunks)
        if extraction_id is None:
            return _achain(head, chunks)
        await response.aclose()
        extraction = _Extraction(
            extraction_id, response.url, self._extraction_timeout, wait.start
        )
        wait.queued(extraction_id, self._extraction_timeout)
        status = extraction.status(_text(head), str(response.url))
        while not extraction.available(status):
            await asyncio.sleep(extraction.pause())
            status = await self.__status(client, extraction)
        response = await self.__get(
            client, stack, extraction.data_url, self._headers
        )
        await _araise_for_status(response)
        return adecompress_gzip(
            response.aiter_bytes(chunk_size), response.request
        )

    async def __status(
        self, client: httpx.AsyncClient, extraction: _Extraction
    ) -> str:
        """Checks the status of an extraction."""
        response = await client.get(
            extraction.status_url, headers=self._headers, timeout=self._timeout
        )
        response.raise_for_status()
        text = _body_text(response)
        return extraction.status(text, extraction.status_url)

    async def __get(
        self,
        client: httpx.AsyncClient,
        stack: contextlib.AsyncExitStack,
        url: str,
        headers: dict[str, str],
    ) -> httpx.Response:
        """Requests a URL; the response is closed as the stack is."""
        return await stack.enter_async_context(
            client.stream("GET", url, headers=headers, timeout=self._timeout)
        )

    async def _fetch(self, query: str, format: str) -> bytes:
        # As LenientRestService._fetch, it decompresses a gzip body sent
        # without a Content-Encoding header
        headers = {**self._headers, "Accept": format}
        async with httpx.AsyncClient(
            verify=self._ssl_context, follow_redirects=True
        ) as client:
            try:
                response = await client.get(
                    _url(self._api_endpoint, query),
                    headers=headers,
                    timeout=self._timeout,
                )
                response.raise_for_status()
                return b"".join(
                    decompress_gzip([response.content], response.request)
                )
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)
