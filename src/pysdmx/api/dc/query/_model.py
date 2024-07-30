"""Objects related to data queries."""

from datetime import datetime
from enum import Enum
from typing import Literal, Optional, Sequence, Union

from msgspec import Struct


class SortBy(Struct, frozen=True):
    """The desired sort order.

    Attributes:
        component: The ID of the component to be used for sorting.
        order: The sorting order (ascending or descending).
    """

    component: str
    order: Literal["asc", "desc"] = "asc"


class Operator(Enum):
    """The list of operators."""

    EQUALS = "="
    NOT_EQUALS = "<>"
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN_OR_EQUAL = ">="
    LIKE = "LIKE"
    NOT_LIKE = "NOT LIKE"
    IN = "IN"
    NOT_IN = "NOT IN"
    BETWEEN = "BETWEEN"
    NOT_BETWEEN = "NOT BETWEEN"
    NULL = "IS NULL"
    NOT_NULL = "IS NOT NULL"


class LogicalOperator(Enum):
    """The list of logical operators."""

    AND = "AND"
    OR = "OR"


class TextFilter(Struct, frozen=True, tag=True):
    """A filter on a text field (char, varchar, etc.)."""

    field: str
    operator: Operator
    value: Union[Sequence[str], str]


class NumberFilter(Struct, frozen=True, tag=True):
    """A filter on a number field (int, long, float, double, etc)."""

    field: str
    operator: Operator
    value: Union[Sequence[Union[int, float]], int, float]


class DateTimeFilter(Struct, frozen=True, tag=True):
    """A filter on a date or datetime field."""

    field: str
    operator: Operator
    value: Union[Sequence[datetime], datetime]


class BooleanFilter(Struct, frozen=True, tag=True):
    """A filter on a boolean field."""

    field: str
    operator: Operator
    value: Optional[bool]


class NullFilter(Struct, frozen=True, tag=True):
    """A filter on null values."""

    field: str
    operator: Operator
    type_hint: Optional[Literal["text", "number", "datetime", "boolean"]] = (
        None
    )


Filter = Union[
    BooleanFilter,
    DateTimeFilter,
    "MultiFilter",
    "NotFilter",
    NullFilter,
    NumberFilter,
    TextFilter,
]


class MultiFilter(Struct, frozen=True, tag=True):
    """A combination of data filters.

    This is useful to combine several conditions, for example
    to indicate that the value for a component must start with an A
    and end with a 10 (e.g. AZB56710).

    Attributes:
        filters: The list of conditions to be applied.
        operator: Whether the conditions are cumulative (AND) or
            exclusive (OR).
    """

    filters: Sequence[Filter]
    operator: LogicalOperator = LogicalOperator.AND


class NotFilter(Struct, frozen=True, tag=True):
    """A filter matching anything but the supplied filter."""

    filter: Filter


__all__ = [
    "BooleanFilter",
    "DateTimeFilter",
    "Filter",
    "MultiFilter",
    "NotFilter",
    "NullFilter",
    "NumberFilter",
    "Operator",
    "SortBy",
    "TextFilter",
]
