"""Collection of SDMX-JSON schemas for content constraints."""

from datetime import datetime
from typing import Dict, Literal, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import MaintainableType
from pysdmx.model import (
    ConstraintAttachment,
    CubeKeyValue,
    CubeRegion,
    CubeValue,
    DataConstraint,
    DataKey,
    DataKeyValue,
    KeySet,
)


class JsonValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a cube value."""

    value: str
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None

    def to_model(self) -> CubeValue:
        """Returns the requested cube value."""
        return CubeValue(self.value, self.validFrom, self.validTo)


class JsonKeyValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of allowed values per component."""

    id: str
    values: Sequence[JsonValue]
    # Additional properties are supported in the model (include,
    # removePrefix, validFrom, validTo, timeRange) but not by the FMR. Therefore,
    # they are ignored for now.

    def to_model(self) -> CubeKeyValue:
        """Returns the requested list of values."""
        return CubeKeyValue(self.id, [v.to_model() for v in self.values])


class JsonCubeRegion(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a cube region."""

    # The property `components` is ignored as it's not used in the FMR`
    keyValues: Sequence[JsonKeyValue]
    include: bool = True

    def to_model(self) -> CubeKeyValue:
        """Returns the requested list of values."""
        return CubeRegion(
            [kv.to_model() for kv in self.keyValues], self.include
        )


class JsonConstraintAttachment(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a constraint attachment."""

    dataProvider: Optional[str]
    dataStructures: Optional[Sequence[str]] = None
    dataflows: Optional[Sequence[str]] = None
    provisionAgreements: Optional[Sequence[str]] = None

    def to_model(self) -> ConstraintAttachment:
        return ConstraintAttachment(
            self.dataProvider,
            self.dataStructures,
            self.dataflows,
            self.provisionAgreements,
        )


class JsonDataKeyValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data key value."""

    id: str
    value: str

    def to_model(self) -> DataKeyValue:
        return DataKeyValue(self.id, self.value)


class JsonDataKey(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data key."""

    keysValues: Sequence[JsonDataKeyValue]
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None

    def to_model(self) -> DataKey:
        return DataKey(
            [kv.to_model() for kv in self.keysValues],
            self.validFrom,
            self.validTo,
        )


class JsonKeySet(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a keyset."""

    isIncluded: bool
    keys: Sequence[JsonDataKey]

    def to_model(self) -> DataKey:
        return KeySet([k.to_model() for k in self.keys], self.isIncluded)


class JsonDataConstraint(MaintainableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a content constraint."""

    role: Optional[Literal["Allowed", "Actual"]] = None
    constraintAttachment: Optional[JsonConstraintAttachment] = None
    cubeRegions: Sequence[JsonCubeRegion] = ()
    dataKeySets: Sequence[JsonKeySet] = ()

    def to_model(self) -> DataConstraint:
        """Converts a JsonDataConstraint to a pysdmx Data Constraint."""
        return DataConstraint(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            annotations=tuple([a.to_model() for a in self.annotations]),
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            role=self.role,
            constraint_attachment=self.constraintAttachment.to_model(),
            cube_regions=[r.to_model() for r in self.cubeRegions],
            key_sets=[s.to_model() for s in self.dataKeySets],
        )


class JsonDataConstraints(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for data constraints."""

    contentConstraints: Sequence[JsonDataConstraint] = ()

    def to_model(self) -> Sequence[DataConstraint]:
        """Returns the requested data constraints."""
        return [cc.to_model() for cc in self.contentConstraints]


class JsonDataConstraintMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /dataconstraint queries."""

    data: JsonDataConstraints

    def to_model(self) -> Sequence[DataConstraint]:
        """Returns the requested data constraints."""
        return self.data.to_model()
