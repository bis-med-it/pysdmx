from parsy import (  # type: ignore[import-untyped]
    from_enum,
    match_item,
    regex,
    seq,
    string,
)

from pysdmx.api.dc.query._model import Operator
from pysdmx.api.dc.query._parsing_model import (
    _CoreOperator,
    _Filter,
    _InOperator,
    _RangeOperator,
)
from pysdmx.api.dc.query._parsing_util import (
    _field,
    _in_vals,
    _pad,
    _to_response,
    _value,
)


def __up(input: str) -> str:
    return input.upper()


__lparen = match_item("(")
__rparen = match_item(")")

__co_op = from_enum(_CoreOperator, transform=__up)
__in_op = regex(r"(?i:NOT)?\s*(?i:IN){1}").map(__up).map(_InOperator)
__ra_op = regex(r"(?i:NOT)?\s*(?i:BETWEEN){1}").map(__up).map(_RangeOperator)


__between_vals = _value.sep_by(
    _pad + string("AND", transform=__up) + _pad,
    min=2,
    max=2,
)

__core_parser = seq(
    field=_pad >> _field << _pad,
    operator=__co_op.map(lambda o: Operator[o.name]),
    value=_pad >> _value << _pad,
).combine_dict(_Filter)

__in_parser = seq(
    field=_pad >> _field << _pad,
    operator=__in_op.map(lambda o: Operator[o.name]),
    value=_pad >> __lparen >> _in_vals << __rparen << _pad,
).combine_dict(_Filter)

__range_parser = seq(
    field=_pad >> _field << _pad,
    operator=__ra_op.map(lambda o: Operator[o.name]),
    value=_pad >> __between_vals << _pad,
).combine_dict(_Filter)


__single_parser = __core_parser | __in_parser | __range_parser
sql_parser = __single_parser.sep_by(
    _pad + string("AND", transform=__up) + _pad, min=1
).map(_to_response)

__all__ = ["sql_parser"]
