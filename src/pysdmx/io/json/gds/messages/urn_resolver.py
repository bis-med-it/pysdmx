"""Collection of GDS-JSON schemas for GDS urn_resolver."""

from typing import List

from msgspec import Struct

from pysdmx.model.gds import GdsUrnResolver, ResolverResult


class JsonUrnResolverMessage(Struct, frozen=True):
    """SDMX-JSON payload for /urn_resolver queries."""

    agency_id: str
    resource_id: str
    version: str
    sdmx_type: str
    resolver_results: List[ResolverResult]

    def to_model(self) -> GdsUrnResolver:
        """Returns a GdsUrnResolver object."""
        return GdsUrnResolver(
            agency_id=self.agency_id,
            resource_id=self.resource_id,
            version=self.version,
            sdmx_type=self.sdmx_type,
            resolver_results=self.resolver_results,
        )
