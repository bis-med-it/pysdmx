import zlib
from typing import (
    AsyncGenerator,
    AsyncIterable,
    Generator,
    Iterable,
    NoReturn,
    Optional,
    Union,
)

import httpx

from pysdmx import errors

# First bytes of a gzip stream
GZIP_MAGIC = b"\x1f\x8b"


def map_httpx_errors(
    e: Union[httpx.RequestError, httpx.HTTPStatusError],
) -> NoReturn:
    """Map httpx errors to pysdmx errors."""
    q = e.request.url
    if isinstance(e, httpx.HTTPStatusError):
        s = e.response.status_code
        t = e.response.text
        if s == 404:
            msg = (
                "The requested resource(s) could not be found in the "
                f"targeted service. The query was `{q}`"
            )
            raise errors.NotFound("Not found", msg) from e
        elif s < 500:
            msg = (
                f"The query returned a {s} error code. The query "
                f"was `{q}`. The error message was: `{t}`."
            )
            raise errors.Invalid(f"Client error {s}", msg) from e
        else:
            msg = (
                f"The service returned a {s} error code. The query "
                f"was `{q}`. The error message was: `{t}`."
            )
            raise errors.InternalError(f"Service error {s}", msg) from e
    else:
        msg = (
            f"There was an issue connecting to the targeted service. "
            f"The query was `{q}`. The error message was: `{e}`."
        )
        raise errors.Unavailable("Connection error", msg) from e


class _GzipDecoder:
    """Decompresses an HTTP body if its first bytes are a gzip stream's.

    httpx decodes the body from its Content-Encoding, but some services
    (e.g. Eurostat) send a gzip body without one. As httpx's decoders do,
    it raises httpx.DecodingError if the gzip stream is invalid.
    """

    def __init__(self, request: httpx.Request) -> None:
        self.__request = request
        self.__head = b""
        self.__gzip: Optional[bool] = None
        self.__decompressor: Optional["zlib._Decompress"] = None

    def decode(self, data: bytes) -> bytes:
        """Returns the part of the body the data holds."""
        if self.__gzip is None:
            data = self.__head + data
            if len(data) < len(GZIP_MAGIC):
                self.__head = data
                return b""
            self.__head = b""
            self.__gzip = data.startswith(GZIP_MAGIC)
        if not self.__gzip:
            return data
        try:
            return self.__decompress(data)
        except zlib.error as e:
            raise httpx.DecodingError(str(e), request=self.__request) from e

    def __decompress(self, data: bytes) -> bytes:
        # A gzip stream may hold several members, one after the other
        out = []
        while data:
            if self.__decompressor is None:
                self.__decompressor = zlib.decompressobj(16 + zlib.MAX_WBITS)
            out.append(self.__decompressor.decompress(data))
            data = self.__decompressor.unused_data
            if self.__decompressor.eof:
                self.__decompressor = None
        return b"".join(out)

    def flush(self) -> bytes:
        """Returns the rest of the body, once all the data is decoded."""
        if self.__decompressor is not None:
            raise httpx.DecodingError(
                "Compressed file ended before the end-of-stream marker was "
                "reached",
                request=self.__request,
            )
        return self.__head


def decompress_gzip(
    chunks: Iterable[bytes], request: httpx.Request
) -> Generator[bytes, None, None]:
    """Decompresses the chunks of an HTTP body sent gzipped.

    Args:
        chunks: The chunks of the body, decoded from its Content-Encoding.
        request: The request of the response, for the errors.

    Yields:
        The chunks of the body, decompressed if its first bytes are a gzip
        stream's, or as they are otherwise.

    Raises:
        httpx.DecodingError: If the gzip stream is invalid.
    """
    decoder = _GzipDecoder(request)
    for chunk in chunks:
        if data := decoder.decode(chunk):
            yield data
    if data := decoder.flush():
        yield data


async def adecompress_gzip(
    chunks: AsyncIterable[bytes], request: httpx.Request
) -> AsyncGenerator[bytes, None]:
    """Decompresses the chunks of an HTTP body sent gzipped.

    The asynchronous counterpart of decompress_gzip.

    Args:
        chunks: The chunks of the body, decoded from its Content-Encoding.
        request: The request of the response, for the errors.

    Yields:
        The chunks of the body, decompressed if its first bytes are a gzip
        stream's, or as they are otherwise.

    Raises:
        httpx.DecodingError: If the gzip stream is invalid.
    """
    decoder = _GzipDecoder(request)
    async for chunk in chunks:
        if data := decoder.decode(chunk):
            yield data
    if data := decoder.flush():
        yield data


class BearerAuth(httpx.Auth):
    """Authenticate requests using a bearer access token.

    This auth class adds an ``Authorization`` header with the value
    ``Bearer <token>`` to outgoing HTTP requests.

    Args:
        token: The bearer access token to send with each request.
    """

    def __init__(self, token: str):
        """Initialize bearer-token authentication.

        Args:
            token: The bearer access token to send with each request.
        """
        self._token = token

    def auth_flow(
        self, request: httpx.Request
    ) -> Generator[httpx.Request, httpx.Response, None]:
        """Apply bearer-token authentication to an outgoing request.

        Args:
            request: The HTTP request being prepared by ``httpx``.

        Yields:
            The modified request including the ``Authorization`` header.
        """
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request
