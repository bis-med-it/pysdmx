"""Model for SDMX Data Constraints."""

from datetime import datetime
from typing import Literal, Optional, Sequence

from msgspec import Struct

from pysdmx.model.__base import MaintainableArtefact


class CubeValue(Struct, frozen=True, omit_defaults=True):
    """A value of the cube, with optional business validity."""

    value: str
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class CubeKeyValue(Struct, frozen=True, omit_defaults=True):
    """The list of values for a cube's component."""

    id: str
    values: Sequence[CubeValue]


class CubeRegion(Struct, frozen=True, omit_defaults=True):
    """A cube region, with its associated values (by default, included)."""

    key_values: Sequence[CubeKeyValue]
    is_included: bool = True


class ConstraintAttachment(Struct, frozen=True, omit_defaults=True):
    """The artefacts to which the data constraint is attached."""

    data_provider: Optional[str]
    data_structures: Optional[Sequence[str]] = None
    dataflows: Optional[Sequence[str]] = None
    provision_agreements: Optional[Sequence[str]] = None


class DataKeyValue(Struct, frozen=True, omit_defaults=True):
    """A key value, i.e. a component of the key (e.g. FREQ=M)."""

    id: str
    value: str


class DataKey(Struct, frozen=True, omit_defaults=True):
    """A data key, i.e. one value per dimension in the data key."""

    keys_values: Sequence[DataKeyValue]
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class KeySet(Struct, frozen=True, omit_defaults=True):
    """A set of keys, inluded by default."""

    keys: Sequence[DataKey]
    is_included: bool


class DataConstraint(MaintainableArtefact, frozen=True, omit_defaults=True):
    """A data constraint, defining the allowed or available values."""

    constraint_attachment: Optional[ConstraintAttachment] = None
    role: Literal["Allowed", "Actual"] = "Allowed"
    cube_regions: Sequence[CubeRegion] = ()
    key_sets: Sequence[KeySet] = ()
