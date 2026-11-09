"""A streamed HTTP body for respx mocks."""

import httpx


class ByteChunks(httpx.SyncByteStream):
    """A response body served in chunks, optionally failing at the end.

    It records how many chunks it has yielded and whether it was closed.
    """

    def __init__(self, chunks, fail=False):
        """Serves the given chunks, then fails if ``fail`` is set."""
        self.chunks = chunks
        self.fail = fail
        self.closed = False
        self.yielded = 0

    def __iter__(self):
        """Yields the chunks."""
        for chunk in self.chunks:
            self.yielded += 1
            yield chunk
        if self.fail:
            raise httpx.ReadError("connection lost")

    def close(self):
        """Records that the stream was closed."""
        self.closed = True


def split(body, size):
    """Splits bytes into chunks of the given size."""
    return [body[i : i + size] for i in range(0, len(body), size)]
