"""Lenient connectors to SDMX-REST services."""

import codecs
import contextlib
import threading
import time
import warnings
from typing import (
    AsyncGenerator,
    AsyncIterable,
    Generator,
    Iterable,
    Optional,
)

import httpx

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


def _still_waiting(what: str, start: float, timeout: Optional[float]) -> str:
    """Builds the message of a warning about a long wait."""
    elapsed = round(time.monotonic() - start)
    limit = "" if timeout is None else f" (timeout: {timeout:g} seconds)"
    return f"{what} after {elapsed} seconds{limit}"


class _WaitWarnings:
    """Warns, while a block runs, that the service is taking long to answer.

    The block is blocked itself, so the warnings are emitted from a thread.
    """

    def __init__(self, url: str, timeout: Optional[float]) -> None:
        self.__what = f"Still waiting for {url} to start sending the message"
        self.__timeout = timeout
        self.__start = time.monotonic()
        self.__done = threading.Event()
        self.__thread = threading.Thread(target=self.__warn, daemon=True)

    def __enter__(self) -> None:
        self.__thread.start()

    def __exit__(self, *args: object) -> None:
        self.__done.set()
        self.__thread.join()

    def __warn(self) -> None:
        wait = _WARN_AFTER
        while not self.__done.wait(wait):
            warnings.warn(
                _still_waiting(self.__what, self.__start, self.__timeout),
                UserWarning,
                stacklevel=1,
            )
            wait = _WARN_EVERY


class LenientRestService(RestService):
    """A lenient synchronous connector to SDMX-REST services.

    It is instantiated and used as the
    :class:`~pysdmx.api.qb.RestService`, which is strict: it expects the
    service to be protocol-correct. This connector also accepts the
    following deviations:

    * A response body compressed with gzip, but sent without a
      ``Content-Encoding`` header (e.g. by Eurostat's SDMX API), is
      decompressed if its first bytes are those of a gzip stream.
    """

    def stream_message(self, url: str) -> Generator[str, None, None]:
        """Streams the text of the SDMX message found at a URL.

        The URL is requested as it is, whatever the endpoint of the service
        is. If the service answers with an error status and an XML body, as
        an SDMX-ML error message, the body is streamed as the message, so
        that the error it describes can be read.

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
            InternalError: If the service answers with a server error.
            Unavailable: If the service cannot be reached, or the response
                cannot be decoded.
        """
        with httpx.Client(
            verify=self._ssl_context, follow_redirects=True
        ) as client:
            try:
                with contextlib.ExitStack() as stack:
                    with _WaitWarnings(url, self._timeout):
                        response = stack.enter_context(
                            client.stream(
                                "GET",
                                url,
                                headers=self._headers,
                                timeout=self._timeout,
                            )
                        )
                    try:
                        response.raise_for_status()
                    except httpx.HTTPStatusError:
                        # The body of an error is read whole: it is small,
                        # and map_httpx_errors needs it
                        response.read()
                        if "<?xml" in response.text:
                            yield response.text
                            return
                        raise
                    yield from codecs.iterdecode(
                        self._decode(response.iter_bytes(), response.request),
                        response.encoding or "utf-8",
                        errors="replace",
                    )
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                map_httpx_errors(e)

    def _decode(
        self, chunks: Iterable[bytes], request: httpx.Request
    ) -> Generator[bytes, None, None]:
        # httpx decodes the body from its Content-Encoding, but some
        # services (e.g. Eurostat) send a gzip body without one
        return decompress_gzip(chunks, request)


class AsyncLenientRestService(AsyncRestService):
    """A lenient asynchronous connector to SDMX-REST services.

    It is instantiated and used as the
    :class:`~pysdmx.api.qb.AsyncRestService`, which is strict, but it also
    accepts the same deviations as the
    :class:`~pysdmx.api.qb.LenientRestService`.
    """

    def _decode(
        self, chunks: Iterable[bytes], request: httpx.Request
    ) -> Generator[bytes, None, None]:
        return decompress_gzip(chunks, request)

    def _adecode(
        self, chunks: AsyncIterable[bytes], request: httpx.Request
    ) -> AsyncGenerator[bytes, None]:
        return adecompress_gzip(chunks, request)
