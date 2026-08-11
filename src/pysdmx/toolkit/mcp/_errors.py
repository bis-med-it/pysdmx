"""Translation of pysdmx errors into agent-actionable MCP errors.

``NotFound`` and ``Unavailable`` mean very different things to an agent
deciding whether to retry, so the error hierarchy is preserved rather
than collapsed into a generic failure. Every error carries a
machine-readable kind, a retriable flag and a hint about what to do next.
"""

# ruff: noqa: E402
from typing import Any, Dict, Optional, Tuple, Type

from pysdmx.__extras_check import __check_mcp_extra

__check_mcp_extra()

from fastmcp.exceptions import ToolError

from pysdmx import errors

#: Maps a pysdmx exception type to ``(kind, retriable, next_step)``.
#:
#: Consulted most-specific first, because ``Unavailable`` subclasses
#: ``RetriableError`` and every error subclasses ``PysdmxError``. Only
#: ``RetriableError`` and its subclasses are marked retriable: pysdmx
#: documents ``InternalError`` as non-retriable, stating that clients
#: should investigate before repeating the query.
_ERROR_TABLE: Tuple[Tuple[Type[Exception], str, bool, str], ...] = (
    (
        errors.Unavailable,
        "unavailable",
        True,
        "The service could not be reached. This is transient - retry "
        "after a short delay, or allow a longer timeout.",
    ),
    (
        errors.NotFound,
        "not_found",
        False,
        "The requested resource does not exist on this service. Call "
        "search_dataflows to list what is actually available. Do not "
        "retry the same reference.",
    ),
    (
        errors.Unauthorized,
        "unauthorized",
        False,
        "The service rejected the credentials. A client certificate may "
        "be required. Do not retry without changing the credentials.",
    ),
    (
        errors.NotImplemented,
        "not_implemented",
        False,
        "This service does not implement the required part of the "
        "SDMX-REST v2 API. Try a different service.",
    ),
    (
        errors.Invalid,
        "invalid_request",
        False,
        "The service rejected the request as malformed. Check the "
        "filter syntax: use AND only (never OR), quote code values, and "
        "use IN (...) for several values of one component. Call "
        "inspect_dataflow to confirm component and code IDs.",
    ),
    (
        errors.InternalError,
        "internal_error",
        False,
        "The service failed, or returned a response that could not be "
        "parsed. Do not repeat the identical call - narrow the filter "
        "or try a different dataflow, since the fault is server-side.",
    ),
    (
        errors.RetriableError,
        "retriable_error",
        True,
        "A transient failure occurred. Retry after a short delay.",
    ),
    (
        errors.PysdmxError,
        "sdmx_error",
        False,
        "The SDMX library reported an error. Inspect the detail for the "
        "underlying cause.",
    ),
)

_UNEXPECTED_HINT = (
    "This is a fault in the pysdmx MCP server rather than in the SDMX "
    "service. Report it with the message above."
)


def classify(exc: Exception) -> Dict[str, Any]:
    """Classify an exception against the pysdmx error hierarchy.

    Args:
        exc: The exception raised by a connector call.

    Returns:
        A dictionary with the keys ``error``, ``retriable``, ``message``,
        ``detail`` and ``next_step``. Exceptions outside the pysdmx
        hierarchy are reported as ``unexpected_error``, deliberately
        distinct from ``internal_error`` so that an agent can tell a
        service fault from a bug in this server.
    """
    for exc_type, kind, retriable, hint in _ERROR_TABLE:
        if isinstance(exc, exc_type):
            return {
                "error": kind,
                "retriable": retriable,
                "message": _summary(exc),
                "detail": _detail(exc),
                "next_step": hint,
            }
    return {
        "error": "unexpected_error",
        "retriable": False,
        "message": _summary(exc),
        "detail": type(exc).__name__,
        "next_step": _UNEXPECTED_HINT,
    }


def as_tool_error(exc: Exception) -> ToolError:
    """Convert an exception into a tool error an agent can act on.

    Args:
        exc: The exception to convert.

    Returns:
        A ``ToolError`` whose message embeds the classification, so that
        the discriminator survives transport to clients that do not
        propagate structured error payloads.
    """
    info = classify(exc)
    detail = f" - {info['detail']}" if info["detail"] else ""
    retriable = str(info["retriable"]).lower()
    return ToolError(
        f"[{info['error']}] {info['message']}{detail} "
        f"| retriable={retriable} | next_step: {info['next_step']}"
    )


def _summary(exc: Exception) -> str:
    """Extract the short title from a pysdmx error, or fall back to str."""
    title = getattr(exc, "title", None)
    if isinstance(title, str) and title:
        return title
    return str(exc) or type(exc).__name__


def _detail(exc: Exception) -> Optional[str]:
    """Extract the long-form description from a pysdmx error, if present."""
    description = getattr(exc, "description", None)
    if isinstance(description, str) and description:
        return description
    return None
