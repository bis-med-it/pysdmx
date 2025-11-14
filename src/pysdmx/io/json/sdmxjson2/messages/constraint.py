"""Collection of SDMX-JSON schemas for content constraints."""

from datetime import datetime
from typing import Dict, Literal, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import MaintainableType


class JsonValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for an allowed value."""

    value: str
    cascadeValues: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None


class JsonKeyValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of allowed values per component."""

    id: str
    values: Sequence[JsonValue]
    # Additional properties are supported in the model (include,
    # removePrefix, validFrom, validTo, timeRange) but not by the FMR. Therefore,
    # they are ignored for now.

    def to_model(self) -> Sequence[str]:
        """Returns the requested list of values."""
        return [v.value for v in self.values]


class JsonCubeRegion(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a cube region."""

    # The property `components` is ignored as it's not used in the FMR`
    keyValues: Sequence[JsonKeyValue]
    include: bool = True

    def to_map(self) -> Dict[str, Sequence[str]]:
        """Gets the list of allowed values for a component."""
        return {kv.id: kv.to_model() for kv in self.keyValues}


class JsonConstraintAttachment(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a constraint attachment."""

    dataProvider: Optional[str]
    dataStructures: Optional[Sequence[str]] = None
    dataflows: Optional[Sequence[str]] = None
    provisionAgreements: Optional[Sequence[str]] = None


class JsonDataKeyValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data key value."""

    id: str
    value: str


class JsonDataKey(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data key."""

    keysValues: Sequence[JsonDataKeyValue]
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None


class JsonKeySet(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a keyset."""

    isIncluded: bool
    keys: Sequence[JsonDataKey]


class JsonDataConstraint(MaintainableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a content constraint."""

    role: Optional[Literal["Allowed", "Actual"]] = None
    constraintAttachment: Optional[JsonConstraintAttachment] = None
    cubeRegions: Optional[Sequence[JsonCubeRegion]] = None
    dataKeySets: Optional[Sequence[JsonKeySet]] = None
