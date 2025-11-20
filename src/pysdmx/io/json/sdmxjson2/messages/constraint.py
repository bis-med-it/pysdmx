"""Collection of SDMX-JSON schemas for content constraints."""

from datetime import datetime
from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    MaintainableType,
)
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
        """Converts a JsonValue to a CubeValue."""
        return CubeValue(self.value, self.validFrom, self.validTo)

    @classmethod
    def from_model(self, cv: CubeValue) -> "JsonValue":
        """Converts a pysdmx cube value to an SDMX-JSON one."""
        return JsonValue(cv.value, cv.valid_from, cv.valid_to)


class JsonKeyValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of allowed values per component."""

    id: str
    values: Sequence[JsonValue]
    # Additional properties are supported in the model (include,
    # removePrefix, validFrom, validTo, timeRange) but not by the FMR.
    # Therefore, they are ignored for now.

    def to_model(self) -> CubeKeyValue:
        """Converts a JsonKeyValue to a CubeKeyValue."""
        return CubeKeyValue(self.id, [v.to_model() for v in self.values])

    @classmethod
    def from_model(self, key_value: CubeKeyValue) -> "JsonKeyValue":
        """Converts a pysdmx cube key value to an SDMX-JSON one."""
        return JsonKeyValue(
            key_value.id, [JsonValue.from_model(v) for v in key_value.values]
        )


class JsonCubeRegion(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a cube region."""

    # The property `components` is ignored as it's not used in the FMR`
    keyValues: Sequence[JsonKeyValue]
    include: bool = True

    def to_model(self) -> CubeRegion:
        """Converts a JsonCubeRegion to a CubeRegion."""
        return CubeRegion(
            [kv.to_model() for kv in self.keyValues], self.include
        )

    @classmethod
    def from_model(self, region: CubeRegion) -> "JsonCubeRegion":
        """Converts a pysdmx cube region to an SDMX-JSON one."""
        return JsonCubeRegion(
            [JsonKeyValue.from_model(kv) for kv in region.key_values],
            region.is_included,
        )


class JsonConstraintAttachment(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a constraint attachment."""

    dataProvider: Optional[str] = None
    dataStructures: Sequence[str] = ()
    dataflows: Sequence[str] = ()
    provisionAgreements: Sequence[str] = ()

    def to_model(self) -> ConstraintAttachment:
        """Converts a JsonConstraintAttachment to a ConstraintAttachment."""
        return ConstraintAttachment(
            self.dataProvider,
            self.dataStructures,
            self.dataflows,
            self.provisionAgreements,
        )

    @classmethod
    def from_model(
        self, attachment: ConstraintAttachment
    ) -> "JsonConstraintAttachment":
        """Converts a pysdmx constraint attachment to an SDMX-JSON one."""
        ds = attachment.data_structures if attachment.data_structures else ()
        df = attachment.dataflows if attachment.dataflows else ()
        pa = (
            attachment.provision_agreements
            if attachment.provision_agreements
            else ()
        )
        return JsonConstraintAttachment(attachment.data_provider, ds, df, pa)


class JsonDataKeyValue(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data key value."""

    id: str
    value: str

    def to_model(self) -> DataKeyValue:
        """Converts a JsonDataKeyValue to a DataKeyValue."""
        return DataKeyValue(self.id, self.value)

    @classmethod
    def from_model(self, kv: DataKeyValue) -> "JsonDataKeyValue":
        """Converts a pysdmx key value to an SDMX-JSON one."""
        return JsonDataKeyValue(kv.id, kv.value)


class JsonDataKey(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a data key."""

    keyValues: Sequence[JsonDataKeyValue]
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None

    def to_model(self) -> DataKey:
        """Converts a JsonDataKey to a DataKey."""
        return DataKey(
            [kv.to_model() for kv in self.keyValues],
            self.validFrom,
            self.validTo,
        )

    @classmethod
    def from_model(self, kv: DataKey) -> "JsonDataKey":
        """Converts a pysdmx key constraint to an SDMX-JSON one."""
        return JsonDataKey(
            [JsonDataKeyValue.from_model(val) for val in kv.keys_values],
            kv.valid_from,
            kv.valid_to,
        )


class JsonKeySet(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a keyset."""

    keys: Sequence[JsonDataKey]
    isIncluded: bool

    def to_model(self) -> KeySet:
        """Converts a JsonKeySet to a KeySet."""
        return KeySet([k.to_model() for k in self.keys], self.isIncluded)

    @classmethod
    def from_model(self, ks: KeySet) -> "JsonKeySet":
        """Converts a pysdmx key set constraint to an SDMX-JSON one."""
        return JsonKeySet(
            [JsonDataKey.from_model(k) for k in ks.keys], ks.is_included
        )


class JsonDataConstraint(MaintainableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a content constraint."""

    constraintAttachment: Optional[JsonConstraintAttachment] = None
    cubeRegions: Optional[Sequence[JsonCubeRegion]] = None
    dataKeySets: Optional[Sequence[JsonKeySet]] = None

    def to_model(self) -> DataConstraint:
        """Converts a JsonDataConstraint to a pysdmx Data Constraint."""
        at = self.constraintAttachment.to_model()  # type: ignore[union-attr]
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
            constraint_attachment=at,
            cube_regions=[r.to_model() for r in self.cubeRegions] if self.cubeRegions else (),
            key_sets=[s.to_model() for s in self.dataKeySets] if self.dataKeySets else (),
        )

    @classmethod
    def from_model(self, cons: DataConstraint) -> "JsonDataConstraint":
        """Converts a pysdmx constraint to an SDMX-JSON one."""
        crs = (
            [JsonCubeRegion.from_model(r) for r in cons.cube_regions]
            if cons.cube_regions
            else None
        )
        dks = (
            [JsonKeySet.from_model(s) for s in cons.key_sets]
            if cons.key_sets
            else None
        )
        return JsonDataConstraint(
            id=cons.id,
            name=cons.name,
            agency=cons.agency,
            description=cons.description,
            version=cons.version,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cons.annotations]
            ),
            isExternalReference=cons.is_external_reference,
            validFrom=cons.valid_from,
            validTo=cons.valid_to,
            constraintAttachment=JsonConstraintAttachment.from_model(
                cons.constraint_attachment
            ),
            cubeRegions=crs,
            dataKeySets=dks,
        )


class JsonDataConstraints(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for data constraints."""

    dataConstraints: Sequence[JsonDataConstraint] = ()

    def to_model(self) -> Sequence[DataConstraint]:
        """Returns the requested data constraints."""
        return [cc.to_model() for cc in self.dataConstraints]


class JsonDataConstraintMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /dataconstraint queries."""

    data: JsonDataConstraints

    def to_model(self) -> Sequence[DataConstraint]:
        """Returns the requested data constraints."""
        return self.data.to_model()
