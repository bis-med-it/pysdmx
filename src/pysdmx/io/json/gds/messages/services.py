"""Collection of GDS-JSON schemas for GDS services."""

from typing import List, Optional, Sequence

from msgspec import Struct

from pysdmx.model.gds import GdsEndpoint, GdsService


class JsonService(Struct, frozen=True):
    """GDS-JSON payload for a service scheme."""

    agencyID: str
    id: str
    name: str
    urn: str
    version: str
    base: str
    endpoints: List[GdsEndpoint]
    authentication: Optional[str] = None

    def to_model(self) -> GdsService:
        """Converts the payload to a GDS Service."""
        return GdsService(
            agency=self.agencyID,
            id=self.id,
            name=self.name,
            urn=self.urn,
            version=self.version,
            base=self.base,
            endpoints=self.endpoints,
            authentication=self.authentication,
        )


class JsonStructures(Struct, frozen=True):
    """Intermediate structure for 'structures' field."""

    services: Sequence[JsonService]


class JsonServiceMessage(Struct, frozen=True):
    """GDS-JSON payload for /service queries."""

    structures: JsonStructures

    def to_model(self) -> Sequence[GdsService]:
        """Returns a list of GdsService objects."""
        return [s.to_model() for s in self.structures.services]
