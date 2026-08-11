"""Service registry and connector construction for the MCP server.

``pysdmx.api.dc.Endpoints`` currently has a single member, ``BIS``, so a
caller-supplied base URL is treated as a first-class input rather than a
fallback: :func:`resolve` accepts a known name or any http(s) URL with
equal standing.

Further SDMX-REST v2 services are deliberately not hardcoded. Each would
need individual verification that it returns structural metadata as
SDMX-JSON 2.0.0 and data as SDMX-CSV, which the connector requires.
Listing them unverified would invite confident failures.
"""

# ruff: noqa: E402
from typing import Dict, Optional
from urllib.parse import urlparse

from pysdmx.__extras_check import __check_data_extra

__check_data_extra()

from pysdmx.api.dc import Endpoints
from pysdmx.api.dc.pd import PandasConnector

#: Socket timeout, in seconds. Higher than the pysdmx default of 20
#: because structural metadata for large dataflows is slow to return.
DEFAULT_TIMEOUT = 60.0

#: Capability notes for services shipped by pysdmx itself.
_KNOWN_NOTES: Dict[str, str] = {
    "BIS": (
        "Bank for International Settlements. Verified working. Reports "
        "series_count but not obs_count. Supports server-side "
        "TIME_PERIOD pushdown. Banking dataflows are very large - "
        "filter before retrieving."
    ),
}


class ResolvedService:
    """A service argument resolved to a usable base URL.

    Attributes:
        name: The display name, such as ``BIS``, or the URL itself for
            caller-supplied services.
        base_url: The SDMX-REST v2 base URL to connect to.
        known: Whether this came from ``pysdmx.api.dc.Endpoints``.
    """

    def __init__(self, name: str, base_url: str, known: bool):
        """Instantiate a resolved service."""
        self.name = name
        self.base_url = base_url
        self.known = known


def known_services() -> Dict[str, str]:
    """Return every service pysdmx ships, as ``{name: base_url}``.

    Returns:
        A mapping read from ``pysdmx.api.dc.Endpoints`` rather than
        hardcoded, so that new pysdmx releases are picked up for free.
    """
    return {member.name: member.value for member in Endpoints}


def notes_for(name: str) -> str:
    """Return the capability notes recorded for a service name.

    Args:
        name: The service name.

    Returns:
        The notes, or a placeholder when none are recorded.
    """
    return _KNOWN_NOTES.get(
        name, "No capability notes recorded for this service."
    )


def resolve(service: Optional[str]) -> ResolvedService:
    """Resolve a service argument to a base URL.

    Args:
        service: A known service name (case-insensitive), an SDMX-REST v2
            base URL, or ``None`` to use the default endpoint.

    Returns:
        The resolved service.

    Raises:
        errors.Invalid: If the argument is neither a known name nor a
            syntactically valid http(s) URL. The message lists the known
            names so the caller can recover without another round trip.
    """
    from pysdmx import errors

    known = known_services()

    if service is None:
        name = next(iter(known))
        return ResolvedService(name, known[name], True)

    candidate = service.strip()
    for name, url in known.items():
        if candidate.upper() == name.upper():
            return ResolvedService(name, url, True)

    parsed = urlparse(candidate)
    if parsed.scheme in ("http", "https") and parsed.netloc:
        return ResolvedService(candidate, candidate.rstrip("/"), False)

    raise errors.Invalid(
        "Unknown service",
        f"{service!r} is neither a known service name "
        f"({sorted(known)}) nor an SDMX-REST v2 base URL. Supply a URL "
        f"starting with http:// or https://.",
    )


def connector(
    resolved: ResolvedService,
    timeout: float = DEFAULT_TIMEOUT,
) -> PandasConnector:
    """Build a connector for a resolved service.

    Connectors are cheap to construct and hold no reusable session state
    worth caching between calls, so this deliberately does not memoise.

    Args:
        resolved: The service to connect to.
        timeout: Socket timeout, in seconds.

    Returns:
        A configured ``PandasConnector``.
    """
    return PandasConnector(resolved.base_url, timeout=timeout)
