"""Classes and parsers for data queries."""

from parsy import ParseError

from pysdmx.errors import ClientError
from pysdmx.api.dc.query._model import (
    BooleanFilter,
    DateTimeFilter,
    Filter,
    LogicalOperator,
    MultiFilter,
    NotFilter,
    NullFilter,
    NumberFilter,
    Operator,
    SortBy,
    TextFilter,
)
from pysdmx.api.dc.query._py_parser import py_parser
from pysdmx.api.dc.query._sql_parser import sql_parser


def parse_query(query: str) -> Filter:
    """Parse a query string into a sequence of filters."""
    try:
        return py_parser.parse(query)  # type: ignore[no-any-return]
    except ParseError:
        try:
            return sql_parser.parse(query)  # type: ignore[no-any-return]
        except ParseError as pe:
            raise ClientError(
                422,
                "Unparseable query",
                (
                    "The query could not be parsed. "
                    "It must be a SQL WHERE clause or "
                    "a Python boolean expression. "
                    f"The query was: {query}"
                ),
            ) from pe


__all__ = [
    "BooleanFilter",
    "DateTimeFilter",
    "LogicalOperator",
    "MultiFilter",
    "NotFilter",
    "NullFilter",
    "NumberFilter",
    "Operator",
    "SortBy",
    "TextFilter",
    "parse_query",
]
