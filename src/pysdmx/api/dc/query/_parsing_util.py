from datetime import timezone
from typing import Sequence, Union

import dateutil
import dateutil.parser
from parsy import digit, regex, string  # type: ignore[import-untyped]

from pysdmx.api.dc.query._model import (
    DateTimeFilter,
    Filter,
    LogicalOperator,
    MultiFilter,
    NumberFilter,
    TextFilter,
)
from pysdmx.api.dc.query._parsing_model import (
    _DateTime,
    _Field,
    _Filter,
    _Number,
    _String,
)


def __map_filter(f: _Filter) -> Filter:
    if isinstance(f.value, list):
        if isinstance(f.value[0], _Number):
            values = [v.value for v in f.value]
            return NumberFilter(f.field.name, f.operator, values)
        elif isinstance(f.value[0], _DateTime):
            values = [v.value for v in f.value]
            return DateTimeFilter(f.field.name, f.operator, values)
        else:
            values = [v.value for v in f.value]
            return TextFilter(f.field.name, f.operator, values)
    elif isinstance(f.value, _Number):
        return NumberFilter(f.field.name, f.operator, f.value.value)
    elif isinstance(f.value, _DateTime):
        return DateTimeFilter(f.field.name, f.operator, f.value.value)
    else:
        return TextFilter(
            f.field.name,
            f.operator,
            f.value.value,  # type: ignore[arg-type,union-attr]
        )


def __map_string(input: str) -> Union[_DateTime, _String]:
    rec = input[1:-1]
    try:
        dt = dateutil.parser.parse(rec)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return _DateTime(dt)
    except dateutil.parser.ParserError:
        return _String(rec)


def _to_response(filters: Sequence[_Filter]) -> Filter:
    if len(filters) == 1:
        return __map_filter(filters[0])
    else:
        flts = [__map_filter(f) for f in filters]
        return MultiFilter(flts, LogicalOperator.AND)


_pad = regex(r"\s*")  # optional whitespace
_field = regex(r"[A-Za-z0-9_@$\-]+").map(_Field)
_int_val = digit.at_least(1).concat().map(int).map(_Number)
_float_val = (
    (digit.many() + string(".").result(["."]) + digit.many())
    .concat()
    .map(float)
    .map(_Number)
)
_string_val = regex(r"'[^']*'").map(__map_string)
_value = _float_val | _int_val | _string_val
_in_vals = _value.sep_by(_pad + string(",") + _pad, min=1)
