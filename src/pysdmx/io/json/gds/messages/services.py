"""Collection of GDS-JSON schemas for GDS services."""

from typing import Sequence

from msgspec import Struct

from pysdmx.model.gds import GdsService


class JsonStructures(Struct, frozen=True):
    """Intermediate structure for 'structures' field."""

    services: Sequence[GdsService]


class JsonServiceMessage(Struct, frozen=True):
    """SDMX-JSON payload for /service queries."""

    structures: JsonStructures

    def to_model(self) -> Sequence[GdsService]:
        """Returns a list of GdsService objects."""
        return self.structures.services
