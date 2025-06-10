"""Collection of GDS-JSON schemas for GDS urn_resolver."""

from typing import List

from msgspec import Struct

from pysdmx.model.gds import GdsUrnResolver, ResolverResult


class JsonUrnResolverResult(Struct, frozen=True):
    """GDS-JSON payload for a single URN resolver result."""

    api_version: str
    query: str
    query_response_status_code: int

    def to_model(self) -> ResolverResult:
        """Returns a ResolverResult object."""
        return ResolverResult(
            api_version=self.api_version,
            query=self.query,
            status_code=self.query_response_status_code,
        )


class JsonUrnResolverMessage(Struct, frozen=True):
    """GDS-JSON payload for /urn_resolver queries."""

    agency_id: str
    resource_id: str
    version: str
    sdmx_type: str
    resolver_results: List[JsonUrnResolverResult]

    def to_model(self) -> GdsUrnResolver:
        """Returns a GdsUrnResolver object."""
        return GdsUrnResolver(
            agency=self.agency_id,
            resource_id=self.resource_id,
            version=self.version,
            sdmx_type=self.sdmx_type,
            resolver_results=[a.to_model() for a in self.resolver_results],
        )
