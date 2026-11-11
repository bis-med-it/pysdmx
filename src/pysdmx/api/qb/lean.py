"""Connector to SDMX-REST services that are not protocol-correct."""

import codecs
from typing import AsyncGenerator, AsyncIterable, Generator, Iterable

import httpx

from pysdmx.api.qb.service import AsyncRestService, RestService
from pysdmx.util._net_utils import (
    adecompress_gzip,
    decompress_gzip,
    map_httpx_errors,
)


class LeanRestService(RestService):
    """Synchronous, lenient connector to SDMX-REST services.

    It is instantiated and used as the
    :class:`~pysdmx.api.qb.RestService`, which expects the service to be
    protocol-correct, but it also copes with the following deviations:

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
                with client.stream(
                    "GET", url, headers=self._headers, timeout=self._timeout
                ) as response:
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


class AsyncLeanRestService(AsyncRestService):
    """Asynchronous, lenient connector to SDMX-REST services.

    It is instantiated and used as the
    :class:`~pysdmx.api.qb.AsyncRestService`, which expects the service to
    be protocol-correct, but it also copes with the same deviations as the
    :class:`~pysdmx.api.qb.LeanRestService`.
    """

    def _decode(
        self, chunks: Iterable[bytes], request: httpx.Request
    ) -> Generator[bytes, None, None]:
        return decompress_gzip(chunks, request)

    def _adecode(
        self, chunks: AsyncIterable[bytes], request: httpx.Request
    ) -> AsyncGenerator[bytes, None]:
        return adecompress_gzip(chunks, request)
