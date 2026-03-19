"""Utility functions to ease the use of SQL Server in pysdmx processes."""

import re
from collections.abc import Collection
from typing import Any, Callable, Literal, Optional, Union

import msgspec

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
from pysdmx.model import (
    Component,
    Components,
    Concept,
    DataflowInfo,
    DataStructureDefinition,
    DataType,
    Facets,
    Role,
    Schema,
)

__SQL_ESC = '"'


class Column(msgspec.Struct):
    """Information about extra columns.

    Attributes:
        id: The column ID
        data_type: The SDMX DataType of the column.
        min_length: The minimum length of the column values.
        max_length: The maximum length of the column values.
        required: Whether a cell may be empty.
        indexed: Whether the column must be indexed.
        in_pk: Whether the column must be added to the composite
            primary key.
        identity: Whether this is a SQL Server identity column
        documentation: Any information to be passed as comment to
            the SQL CREATE TABLE statement.
    """

    id: str
    data_type: DataType
    min_length: Optional[int] = None
    max_length: Optional[int] = None
    required: bool = False
    indexed: bool = False
    in_pk: bool = False
    identity: bool = False
    documentation: Optional[str] = None


def create_table(
    structure: Union[DataflowInfo, DataStructureDefinition, Schema],
    schema_name: str = "dbo",
    table_name: Optional[str] = None,
    pk_fields: Optional[str] = None,
    index_fields: Optional[Collection[str]] = None,
    extra_columns: Optional[Collection[Column]] = None,
) -> str:
    """Return a CREATE statement for the supplied structure.

    Args:
        structure: The structure for which a database table must be created.
        schema_name: The name of the schema to which the new table belongs.
            If it is not supplied, the table will be created in the default
            schema.
        table_name: The name of the table to be created. If it is not supplied,
            the structure ID will be used as table name.
        pk_fields: The field(s) to be used for the (composite) primary key. If
            it is not supplied, the primary key will be a composite key
            combining the dimension values.
        index_fields: The columns for which an index should be created. If it
            is not supplied, indexes will be created for every dimension in the
            supplied structure.
        extra_columns: Any additional column required for the table, beyond the
            ones (i.e. the components) already defined in the structure.

    Returns:
        The CREATE statement for the supplied structure, as a string.
    """
    sn = f"{schema_name}."
    kn = f"{schema_name}_"
    tn = table_name if table_name else structure.id
    cs = f"CREATE TABLE {sn}{tn} (\n"
    comps = list(__order_components(structure.components))
    if extra_columns:
        comps.extend([__map_col_to_comp(col) for col in extra_columns])
    for c in comps:
        nm = f" -- {c.name}" if c.name else ""
        cs += f"    {c.id} {get_sql_data_type(c)} {__map_required(c)},{nm}\n"
    cs += f"    CONSTRAINT PK_{kn}{tn} PRIMARY KEY ("
    if pk_fields:
        cs += ",".join(f for f in pk_fields)
    else:
        cs += ",".join(c.id for c in structure.components.dimensions)
        if extra_columns:
            extra = ",".join(c.id for c in extra_columns if c.in_pk)
            if extra:
                cs += f",{extra}"
    cs += ")\n"
    cs += ");\n"
    index_fields = list(
        (
            index_fields
            if index_fields
            else [c.id for c in structure.components.dimensions]
        )
    )
    if extra_columns:
        index_fields.extend(
            c.id
            for c in extra_columns
            if c.indexed and c.id not in index_fields
        )
    for f in index_fields:
        cs += f"CREATE INDEX IDX_{kn}{tn}_{f} ON {sn}{tn} ({f});\n"
    return cs


def get_select_statement(
    table_name: str,
    schema_name: str = "dbo",
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
    ] = None,
    columns: Optional[Collection[str]] = None,
    sort: Optional[Collection[SortBy]] = None,
    offset: int = 0,
    limit: Optional[int] = None,
) -> tuple[str, list[Any]]:
    """Return a SQL SELECT statement based on the provided input.

    Args:
        table_name: The name of the table from which to fetch data.
        schema_name: The name of the schema to which the table belongs.
        filters: The filters to be considered in the SQL WHERE clause.
        columns: The columns from which to fetch data.
        sort: How to sort data.
        offset: The number of rows to skip before starting to return rows.
        limit: The maximum number of rows to return after the offset.

    Returns: A tuple containing:
        - A string representing the SELECT statement corresponding to the
            supplied input, as a prepared statement.
        - A list of values to replace the placeholders in the prepared
            statement.
    """
    if not __valid_identifier(schema_name) or not __valid_identifier(
        table_name
    ):
        raise errors.Invalid("Invalid table or schema name")

    target = f"{schema_name}.{table_name}"
    where, values = get_where_clause(filters)
    cols = get_select_columns(columns)
    sc = get_sort_clause(sort)
    pag = get_pagination_clause(offset, limit)

    # It is safe to ignore S608, as the input is sanitized.
    return f"SELECT {cols} FROM {target}{where}{sc}{pag}", values  # noqa: S608


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


def get_pagination_clause(offset: int, limit: Optional[int] = None) -> str:
    """Return a string to control pagiunation of the records to be returned.

    Args:
        offset: The number of rows to skip before starting to return rows.
        limit: The maximum number of rows to return after the offset.

    Returns:
        The OFFSET and FETCH string required to paginate results in
            SQL Server, or an empty string otherwise.
    """
    o = offset if offset and offset > 0 else 0
    if limit:
        return f" OFFSET {o} ROWS FETCH NEXT {limit} ROWS ONLY"
    elif o > 0:
        return f" OFFSET {o} ROWS"
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


def get_sql_data_type(c: Component) -> str:
    """Infer the appropriate SQL Server type for the supplied component.

    This function maps the SDMX data types to the SQL Server ones, and uses
    the max_length facet (if any), to infer the column size.

    Returns:
        The appropriate SQL Server type for the supplied component.
    """
    max_length = (
        str(c.facets.max_length)
        if c.facets and c.facets.max_length and c.facets.max_length > 0
        else "MAX"
    )
    equal_length = (
        c.facets
        and c.facets.min_length
        and c.facets.min_length == c.facets.max_length
    )
    # Numeric types
    if c.dtype == DataType.SHORT:
        return "SMALLINT"
    elif c.dtype == DataType.INTEGER:
        return "INT"
    elif c.dtype in (DataType.LONG, DataType.COUNT):
        return "BIGINT"
    elif c.dtype == DataType.BIG_INTEGER:
        return "DECIMAL(38, 0)"
    elif c.dtype == DataType.DECIMAL:
        return "DECIMAL(38, 18)"
    elif c.dtype == DataType.FLOAT:
        return "REAL"
    elif c.dtype == DataType.DOUBLE:
        return "FLOAT"
    # Date / time types
    elif c.dtype in (
        DataType.REP_YEAR,  # 2000-A1
        DataType.REP_SEMESTER,  # 2000-S1
        DataType.REP_TRIMESTER,  # 2000-T1
        DataType.REP_QUARTER,  # 2000-Q1
    ):
        return "CHAR(7)"
    elif c.dtype in (DataType.REP_MONTH, DataType.REP_WEEK):
        return "CHAR(8)"  # 2000-M01, 2000-W01
    elif c.dtype == DataType.REP_DAY:
        return "CHAR(9)"  # 2000-D001
    elif c.dtype in (
        DataType.YEAR,  # ISO 8601 year
        DataType.MONTH,  # ISO 8601 month (--MM)
    ):
        return "VARCHAR(10)"
    elif c.dtype == DataType.DAY:
        return "VARCHAR(11)"  # ISO 8601 day (---DD)
    elif c.dtype in (
        DataType.MONTH_DAY,  # ISO 8601 month-day (--MM-DD)
        DataType.YEAR_MONTH,  # ISO 8601 year-month (2000-01)
    ):
        return "VARCHAR(13)"
    elif c.dtype == DataType.GREGORIAN_TIME_PERIOD:
        return "VARCHAR(16)"  # ISO 8601 Gregorian periods
    elif c.dtype in (
        DataType.STD_TIME_PERIOD,
        DataType.PERIOD,
        DataType.DURATION,
    ):
        return "VARCHAR(50)"
    elif c.dtype == DataType.DATE_TIME:
        return "DATETIME2"
    elif c.dtype == DataType.DATE:
        return "DATE"
    elif c.dtype == DataType.TIME:
        return "TIME"
    elif c.dtype == DataType.BASIC_TIME_PERIOD:
        return "VARCHAR(25)"
    # All other types
    elif c.dtype == DataType.BOOLEAN:
        return "BIT"
    elif (
        c.dtype == DataType.INCREMENTAL
        and c.facets
        and isinstance(c.facets.interval, int)
    ):
        return "INT"
    else:
        if equal_length:
            return f"CHAR({max_length})"
        elif c.dtype == DataType.NUMERIC:
            return f"VARCHAR({max_length})"
        else:
            return f"NVARCHAR({max_length})"


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


def __map_required(c: Component) -> str:
    if (
        c.dtype == DataType.INCREMENTAL
        and c.facets
        and c.facets.is_sequence
        and isinstance(c.facets.interval, int)
    ):
        inc = c.facets.interval if c.facets.interval else 1
        return f"IDENTITY(1,{inc})"
    elif c.role == Role.DIMENSION or c.required:
        return "NOT NULL"
    else:
        return "NULL"


def __match_and_sort(
    attrs: Collection[Component], flt: Callable[[Any], bool]
) -> Collection[Component]:
    return sorted([c for c in attrs if flt(c)], key=lambda x: x.id)


def __order_components(comps: Components) -> Collection[Component]:
    out: list[Component] = []
    out.extend(comps.dimensions)
    out.extend(comps.measures)
    out.extend(  # Add obs-level attributes
        __match_and_sort(
            comps.attributes,
            lambda c: c.attachment_level == "O"
            or len(c.attachment_level.split(",")) == len(comps.dimensions),
        )
    )
    out.extend(  # Then add series-level attributes
        __match_and_sort(
            comps.attributes,
            lambda c: len(c.attachment_level.split(","))
            == len(comps.dimensions) - 1,
        )
    )
    out.extend(  # Then add group-level attributes
        __match_and_sort(
            comps.attributes,
            lambda c: len(c.attachment_level.split(","))
            < len(comps.dimensions) - 1
            and c.attachment_level not in ["D", "O"],
        )
    )
    out.extend(  # Finally, add dataflow-level attributes
        __match_and_sort(
            comps.attributes, lambda c: c.attachment_level.split(",") == "D"
        )
    )
    return out


def __map_col_to_comp(col: Column) -> Component:
    minl = col.min_length
    maxl = col.max_length
    inc = 1 if col.identity else None
    facets = Facets(minl, maxl, interval=inc, is_sequence=col.identity)

    return Component(
        col.id,
        col.required,
        Role.ATTRIBUTE,
        Concept(col.id),
        col.data_type,
        facets,
        name=col.documentation,
        attachment_level="O",
    )


def __valid_identifier(name: str) -> bool:
    """Validate that a string is a valid SQL identifier."""
    return bool(re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", name))
