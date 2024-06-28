from enum import Enum

from parsy import from_enum, regex, seq, string  # type: ignore[import-untyped]

from pysdmx.api.dc.query._model import Operator
from pysdmx.api.dc.query._parsing_model import _Filter
from pysdmx.api.dc.query._parsing_util import (
    _field,
    _in_vals,
    _pad,
    _to_response,
    _value,
)


class _PythonCoreOperator(Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN_OR_EQUAL = ">="


class _PythonInOperator(Enum):
    IN = "in"
    NOT_IN = "not in"


class PythonOperator(Enum):
    EQUALS = "=="
    NOT_EQUALS = "!="
    LESS_THAN = "<"
    GREATER_THAN = ">"
    LESS_THAN_OR_EQUAL = "<="
    GREATER_THAN_OR_EQUAL = ">="
    IN = "in"
    NOT_IN = "not in"


def _to_operator(op: PythonOperator) -> Operator:
    return Operator[op.name]


__lparen = regex(r"[\[\(]{1}")
__rparen = regex(r"[\]\)]{1}")

__co_op = from_enum(_PythonCoreOperator)
__in_op = regex(r"(not)?\s*(in){1}").map(_PythonInOperator)

__core_parser = seq(
    field=_pad >> _field << _pad,
    operator=__co_op.map(_to_operator),
    value=_pad >> _value << _pad,
).combine_dict(_Filter)

__in_parser = seq(
    field=_pad >> _field << _pad,
    operator=__in_op.map(_to_operator),
    value=_pad >> __lparen >> _in_vals << __rparen << _pad,
).combine_dict(_Filter)


__p = __core_parser | __in_parser
py_parser = __p.sep_by(_pad + string("and") + _pad, min=1).map(_to_response)

__all__ = ["py_parser"]
