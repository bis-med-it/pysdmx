"""Model for SDMX Data Constraints."""

from datetime import datetime
from enum import Enum
from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.model.__base import MaintainableArtefact


class CubeValue(Struct, frozen=True, omit_defaults=True):
    """A value of the cube, with optional business validity."""

    value: str
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class TimePeriodBoundary(Struct, frozen=True, omit_defaults=True):
    """One end of a cube-region time range, with inclusivity."""

    period: str
    is_inclusive: bool = True


class CubeTimeRange(Struct, frozen=True, omit_defaults=True):
    """A time range for a cube region's time dimension.

    Mirrors the SDMX TimeRange: a period before, a period after, or a
    start/end range. Only the relevant boundaries are set.
    """

    before_period: Optional[TimePeriodBoundary] = None
    after_period: Optional[TimePeriodBoundary] = None
    start_period: Optional[TimePeriodBoundary] = None
    end_period: Optional[TimePeriodBoundary] = None


class CubeKeyValue(Struct, frozen=True, omit_defaults=True):
    """The list of values (or a time range) for a cube's component.

    Attributes:
        id: The referenced component (e.g. a dimension).
        values: The set of allowed/excluded values.
        time_range: A time range, for a time dimension (mutually
            exclusive with values in SDMX-ML).
        valid_from: Start of the validity period (SDMX-ML 3.0/3.1 only).
        valid_to: End of the validity period (SDMX-ML 3.0/3.1 only).
    """

    id: str
    values: Sequence[CubeValue] = ()
    time_range: Optional[CubeTimeRange] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


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


class ConstraintRole(str, Enum):
    """Whether a data constraint defines allowed or actual content."""

    ALLOWED = "Allowed"
    """The constraint defines the content allowed by the structure."""
    ACTUAL = "Actual"
    """The constraint describes the data actually present."""


class DataConstraint(MaintainableArtefact, frozen=True, omit_defaults=True):
    """A data constraint, defining the allowed or available values."""

    role: ConstraintRole = ConstraintRole.ALLOWED
    constraint_attachment: Optional[ConstraintAttachment] = None
    cube_regions: Sequence[CubeRegion] = ()
    key_sets: Sequence[KeySet] = ()
