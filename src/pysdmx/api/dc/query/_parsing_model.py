from datetime import datetime
from enum import Enum
from typing import Sequence, Union

from msgspec import Struct

from pysdmx.api.dc.query._model import Operator


class _CoreOperator(Enum):
    EQUALS = "="
    NOT_EQUALS = "<>"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN_OR_EQUAL = ">="
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"


class _InOperator(Enum):
    IN = "IN"
    NOT_IN = "NOT IN"


class _RangeOperator(Enum):
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"


class _NullOperator(Enum):
    NULL = "IS NULL"
    NOT_NULL = "IS NOT NULL"


class _Field(Struct, frozen=True):
    name: str


class _Number(Struct, frozen=True):
    value: Union[int, float]


class _String(Struct, frozen=True):
    value: str


class _Boolean(Struct, frozen=True):
    value: bool


class _DateTime(Struct, frozen=True):
    value: datetime


class _Filter(Struct, frozen=True):
    """A data filter."""

    field: _Field
    operator: Operator
    value: Union[
        None,
        _Boolean,
        _DateTime,
        _Number,
        Sequence[_DateTime],
        Sequence[_Number],
        Sequence[_String],
        _String,
    ] = None
