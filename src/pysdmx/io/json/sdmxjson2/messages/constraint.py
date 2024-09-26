"""Collection of SDMX-JSON schemas for content constraints."""

from datetime import datetime
from typing import Dict, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation


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


class JsonDataConstraint(Struct, frozen=True):
    """SDMX-JSON payload for a content constraint."""

    id: str
    name: str
    agency: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Sequence[JsonAnnotation] = None
    isPartial: bool = False
    cubeRegions: Sequence[JsonCubeRegion]
