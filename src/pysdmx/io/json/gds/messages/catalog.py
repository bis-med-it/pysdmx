"""Collection of GDS-JSON schemas for GDS catalogs."""

from typing import Any, List, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.gds.messages.agencies import JsonAgency
from pysdmx.io.json.gds.messages.services import JsonService
from pysdmx.model import Agency
from pysdmx.model.gds import (
    GdsCatalog,
    GdsEndpoint,
    GdsService,
    GdsServiceReference,
)


class JsonCatalog(Struct, frozen=True):
    """GDS-JSON payload for a catalog scheme."""

    agencyID: str
    id: str
    version: str
    name: str
    urn: str
    endpoints: Optional[List[GdsEndpoint]] = None
    serviceRefs: Optional[List[GdsServiceReference]] = None

    def to_model(
        self, agencies: List[Agency], services: List[GdsService]
    ) -> GdsCatalog:
        """Converts the payload to a GDS Catalog."""
        agency = next(
            (a for a in agencies if a.id == self.agencyID),
            self.agencyID,
        )

        catalog_services: Any = services
        if self.serviceRefs:
            catalog_services = catalog_services or []
            catalog_services.extend(
                ref
                for ref in self.serviceRefs
                if ref.short_urn not in {s.short_urn for s in catalog_services}
            )

        return GdsCatalog(
            id=self.id,
            version=self.version,
            name=self.name,
            urn=self.urn,
            agency=agency,
            endpoints=self.endpoints,
            services=catalog_services,
        )


class JsonStructures(Struct, frozen=True):
    """Intermediate structure for 'structures' field."""

    catalogs: Sequence[JsonCatalog]
    agencies: Optional[Sequence[JsonAgency]] = None
    services: Optional[List[JsonService]] = None


class JsonCatalogMessage(Struct, frozen=True):
    """GDS-JSON payload for /catalog queries."""

    structures: JsonStructures

    def to_model(self) -> Sequence[GdsCatalog]:
        """Returns a list of GdsCatalog objects."""
        agencies = [a.to_model() for a in (self.structures.agencies or [])]
        services = [s.to_model() for s in (self.structures.services or [])]

        return [
            c.to_model(agencies=agencies, services=services)
            for c in self.structures.catalogs
        ]
