"""Collection of GDS-JSON schemas for GDS catalogs."""

from typing import List, Optional, Sequence

from msgspec import Struct

from pysdmx.model.gds import GdsCatalog, GdsEndpoint, GdsServiceReference, GdsService


class JsonCatalog(Struct, frozen=True):
    """GDS-JSON payload for a catalog scheme."""

    agencyID: str
    id: str
    version: str
    name: str
    urn: str
    agency: Optional[str] = None
    endpoints: Optional[List[GdsEndpoint]] = None
    services = Optional[List[GdsService]] = None
    serviceRefs: Optional[List[GdsServiceReference]] = None

    def to_model(self) -> GdsCatalog:
        """Converts the payload to a GDS Catalog."""
        services = self.services if self.services else None
        if self.serviceRefs:
            services = []
            for ref in self.serviceRefs:
                urn = ref.urn
                if not any(s.urn == urn for s in services):
                    services.append(ref)

        agency = self.agency if self.agency else self.agencyID

        return GdsCatalog(
            agency=agency,
            id=self.id,
            version=self.version,
            name=self.name,
            urn=self.urn,
            endpoints=self.endpoints,
            services=services,
        )


class JsonStructures(Struct, frozen=True):
    """Intermediate structure for 'structures' field."""

    catalogs: Sequence[JsonCatalog]


class JsonCatalogMessage(Struct, frozen=True):
    """GDS-JSON payload for /catalog queries."""

    structures: JsonStructures

    def to_model(self) -> Sequence[GdsCatalog]:
        """Returns a list of GdsCatalog objects."""
        return [c.to_model() for c in self.structures.catalogs]
