from typing import NoReturn, Union

import httpx

from pysdmx import errors


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

    def auth_flow(self, request: httpx.Request):
        """Apply bearer-token authentication to an outgoing request.

        Args:
            request: The HTTP request being prepared by ``httpx``.

        Yields:
            The modified request including the ``Authorization`` header.
        """
        request.headers["Authorization"] = f"Bearer {self._token}"
        yield request
