"""Collection of GDS-JSON schemas for GDS catalogs."""

from typing import Sequence

from msgspec import Struct

from pysdmx.model.gds import GdsCatalog


class JsonStructures(Struct, frozen=True):
    """Intermediate structure for 'structures' field."""

    catalogs: Sequence[GdsCatalog]


class JsonCatalogMessage(Struct, frozen=True):
    """SDMX-JSON payload for /catalog queries."""

    structures: JsonStructures

    def to_model(self) -> Sequence[GdsCatalog]:
        """Returns a list of GdsCatalog objects."""
        return self.structures.catalogs
