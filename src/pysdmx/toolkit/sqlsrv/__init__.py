"""Utility functions to ease the use of SQL Server in pysdmx processes."""

from collections.abc import Collection
from typing import Any, Optional, Union

from pysdmx import errors
from pysdmx.api.dc.query import (
    BooleanFilter,
    DateTimeFilter,
    MultiFilter,
    NotFilter,
    NullFilter,
    NumberFilter,
    Operator,
    SortBy,
    TextFilter,
)

__SQL_ESC = '"'


def get_select_columns(columns: Optional[Collection[str]]) -> str:
    """Return the columns to be selected from a table.

    This will list the escaped IDs of the columns to be returned
    or will return * if no columns are supplied.

    Args:
        columns: The columns from which to return data, or * if no
            columns are supplied.

    Returns:
        The string to be used directly after SELECT in the SQL query.
    """
    if columns:
        c = [f"{__SQL_ESC}{col}{__SQL_ESC}" for col in columns]
        return ", ".join(c)
    else:
        return "*"


def get_sort_clause(sort: Optional[Collection[SortBy]]) -> str:
    """Return a SQL ORDER BY clause from the provided sort criteria, if any.

    Args:
        sort: The various sort criteria, if any.

    Returns:
        The ORDER BY clause, to sort the data to be return according to the
            sort criteria provided, if any. Else, an empty string is returned.
    """
    if sort:
        s = [
            f"{__SQL_ESC}{c.component}{__SQL_ESC} {c.order.upper()}"
            for c in sort
        ]
        return f" ORDER BY {', '.join(s)}"
    else:
        return ""


def get_pagination_clause(offset: int, limit: Optional[int]) -> str:
    """Return a string to control pagiunation of the records to be returned.

    Args:
        offset: The number of rows to skip before starting to return rows.
        limit: The maximum number of rows to return after the offset.

    Returns:
        The OFFSET and FETCH string required to paginate results in
            SQL Server, or an empty string otherwise.
    """
    if limit:
        o = offset if offset and offset >= 0 else 0
        return f" OFFSET {o} ROWS FETCH NEXT {limit} ROWS ONLY"
    elif offset >= 0:
        return f" OFFSET {offset} ROWS"
    else:
        return ""


def get_where_clause(
    filters: Optional[
        Union[
            BooleanFilter,
            DateTimeFilter,
            MultiFilter,
            NotFilter,
            NullFilter,
            NumberFilter,
            TextFilter,
        ]
    ],
) -> tuple[str, list[Any]]:
    """Return the SQL WHERE clause representing the supplied filters, if any.

    Args:
        filters: The filters to be considered in the SQL WHERE clause.

    Returns:
        A tuple containing:
        - A string representing the SQL WHERE clause with placeholders for the
            filters, or an empty string if no filters are provided.
        - A list of values to replace the placeholders in the prepared
            statement.
    """
    if filters:
        m: list[tuple[str, list[Any]]] = [__get_filter(filters)]
        cf = list(filter(lambda x: len(x[0]) > 0, m))
        sqlstr = [a for a, _ in cf]
        values = []
        for j in cf:
            values.extend(j[1])
        s1 = " AND ".join(sqlstr)
        s2 = f" WHERE {s1}"
        return (s2, values)
    else:
        return ("", [])


def __get_filter(
    flt: Union[
        BooleanFilter,
        DateTimeFilter,
        MultiFilter,
        NotFilter,
        NullFilter,
        NumberFilter,
        TextFilter,
    ],
) -> tuple[str, list[Any]]:
    if isinstance(flt, BooleanFilter):
        return __handle_boolean_filter(flt)
    elif isinstance(flt, NullFilter):
        return __handle_null_filter(flt)
    elif isinstance(flt, MultiFilter):
        return __handle_multi_filter(flt)
    elif isinstance(flt, NotFilter):
        return __handle_not_filter(flt)
    else:
        return __handle_single_filter(flt)


def __handle_single_filter(
    flt: Union[DateTimeFilter, NumberFilter, TextFilter],
) -> tuple[str, list[Any]]:
    # ruff: noqa: C901
    # The complexity is acceptable is it is merely due to the
    # high amount of operators we support.
    if flt.operator == Operator.GREATER_THAN:
        return (f"{__get_field(flt.field)} > ?", [flt.value])
    elif flt.operator == Operator.GREATER_THAN_OR_EQUAL:
        return (f"{__get_field(flt.field)} >= ?", [flt.value])
    elif flt.operator == Operator.LESS_THAN:
        return (f"{__get_field(flt.field)} < ?", [flt.value])
    elif flt.operator == Operator.LESS_THAN_OR_EQUAL:
        return (f"{__get_field(flt.field)} <= ?", [flt.value])
    elif flt.operator == Operator.NOT_EQUALS:
        return (f"{__get_field(flt.field)} <> ?", [flt.value])
    elif flt.operator == Operator.LIKE:
        return (
            f"UPPER({__get_field(flt.field)}) LIKE ?",
            [f"{str(flt.value).replace('*', '%').upper()}"],
        )
    elif flt.operator == Operator.NOT_LIKE:
        return (
            f"UPPER({__get_field(flt.field)}) NOT LIKE ?",
            [f"{str(flt.value).replace('*', '%').upper()}"],
        )
    elif flt.operator == Operator.IN:
        ph = ",".join("?" * len(flt.value))  # type: ignore[arg-type]
        return (
            f"{__get_field(flt.field)} IN ({ph})",
            flt.value,
        )  # type: ignore[return-value]
    elif flt.operator == Operator.NOT_IN:
        ph = ",".join("?" * len(flt.value))  # type: ignore[arg-type]
        return (
            f"{__get_field(flt.field)} NOT IN ({ph})",
            flt.value,
        )  # type: ignore[return-value]
    elif flt.operator == Operator.BETWEEN:
        return (
            f"{__get_field(flt.field)} BETWEEN ? AND ?",
            [flt.value[0], flt.value[1]],  # type: ignore[index]
        )
    elif flt.operator == Operator.NOT_BETWEEN:
        return (
            f"{__get_field(flt.field)} NOT BETWEEN ? AND ?",
            [flt.value[0], flt.value[1]],  # type: ignore[index]
        )
    else:
        return (f"{__get_field(flt.field)} = ?", [flt.value])


def __handle_null_filter(flt: NullFilter) -> tuple[str, list[Any]]:
    if flt.operator == Operator.NULL:
        return (f"{__get_field(flt.field)} IS NULL", [])
    else:
        return (f"{__get_field(flt.field)} IS NOT NULL", [])


def __handle_boolean_filter(flt: BooleanFilter) -> tuple[str, list[Any]]:
    if flt.operator == Operator.EQUALS:
        return (
            f"{__get_field(flt.field)} = {str(flt.value).upper()}",
            [],
        )
    elif flt.operator == Operator.NOT_EQUALS:
        return (
            f"{__get_field(flt.field)} <> {str(flt.value).upper()}",
            [],
        )
    else:
        raise errors.Invalid(
            "Invalid operator",
            "Only equal and not equal can be used in boolean queries.",
            {"operator_used": flt.operator},
        )


def __handle_multi_filter(flt: MultiFilter) -> tuple[str, list[Any]]:
    s = []
    v = []
    for f in flt.filters:
        a, b = __get_filter(f)
        if isinstance(f, MultiFilter):
            s.append(f"({a})")
        else:
            s.append(a)
        v.extend(b)
    w = f" {flt.operator.value} ".join(s)
    return (f"{w}", v)


def __handle_not_filter(flt: NotFilter) -> tuple[str, list[Any]]:
    a, b = __get_filter(flt.filter)
    return (f"NOT({a})", b)


def __get_field(field: str) -> str:
    return f"{__SQL_ESC}{field}{__SQL_ESC}"
