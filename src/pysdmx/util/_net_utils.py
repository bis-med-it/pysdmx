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
