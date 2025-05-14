"""Collection of GDS-JSON schemas for GDS catalogs."""

from typing import List, Optional, Sequence

from msgspec import Struct

from pysdmx.model.gds import GdsCatalog, GdsEndpoint, GdsServiceReference


class JsonCatalog(Struct, frozen=True):
    """GDS-JSON payload for a catalog scheme."""

    agencyID: str
    id: str
    version: str
    name: str
    urn: str
    endpoints: Optional[List[GdsEndpoint]] = None
    serviceRefs: Optional[List[GdsServiceReference]] = None

    def to_model(self) -> GdsCatalog:
        """Converts the payload to a GDS Catalog."""
        return GdsCatalog(
            agency_id=self.agencyID,
            id=self.id,
            version=self.version,
            name=self.name,
            urn=self.urn,
            endpoints=self.endpoints,
            serviceRefs=self.serviceRefs,
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
