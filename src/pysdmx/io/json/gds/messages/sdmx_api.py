"""Collection of GDS-JSON schemas for GDS sdmx_api obj."""

from typing import Sequence

from msgspec import Struct

from pysdmx.model.gds import GdsSdmxApi


class JsonStructures(Struct, frozen=True):
    """Intermediate structure for 'structures' field."""

    sdmxApis: Sequence[GdsSdmxApi]


class JsonSdmxApiMessage(Struct, frozen=True):
    """GDS-JSON payload for /sdmxapi queries."""

    structures: JsonStructures

    def to_model(self) -> Sequence[GdsSdmxApi]:
        """Returns a list of GdsSdmxApi objects."""
        return self.structures.sdmxApis
