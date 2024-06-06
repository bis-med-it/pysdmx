"""Collection of SDMX-JSON schemas for content constraints."""

from typing import Dict, Sequence

from msgspec import Struct


class JsonValue(Struct, frozen=True):
    """SDMX-JSON payload for an allowed value."""

    value: str


class JsonKeyValue(Struct, frozen=True):
    """SDMX-JSON payload for the list of allowed values per component."""

    id: str
    values: Sequence[JsonValue]

    def to_model(self) -> Sequence[str]:
        """Returns the requested list of values."""
        return [v.value for v in self.values]


class JsonCubeRegion(Struct, frozen=True):
    """SDMX-JSON payload for a cube region."""

    keyValues: Sequence[JsonKeyValue]

    def to_map(self) -> Dict[str, Sequence[str]]:
        """Gets the list of allowed values for a component."""
        return {kv.id: kv.to_model() for kv in self.keyValues}


class JsonContentConstraint(Struct, frozen=True):
    """SDMX-JSON payload for a content constraint."""

    cubeRegions: Sequence[JsonCubeRegion]
