from datetime import datetime, timezone
from typing import Sequence

import pytest

from pysdmx.api.dc.query._model import (
    DateTimeFilter,
    LogicalOperator,
    MultiFilter,
    NumberFilter,
    Operator,
    TextFilter,
)
from pysdmx.api.dc.query._parsing_model import (
    _CoreOperator,
    _InOperator,
    _RangeOperator,
)
from pysdmx.api.dc.query._sql_parser import sql_parser


@pytest.fixture
def field() -> str:
    return "OBS_VALUE"


@pytest.fixture
def int_value() -> int:
    return 42


@pytest.fixture
def boolean_value() -> bool:
    return True


@pytest.fixture
def datetime_value() -> str:
    return "2024-05-23"


@pytest.fixture
def float_value() -> float:
    return 42.84


@pytest.fixture
def str_value() -> str:
    return "A"


@pytest.fixture
def int_values() -> Sequence[int]:
    return [42, 83]


@pytest.fixture
def datetime_values() -> Sequence[str]:
    return ["2024-05-01", "2024-05-23"]


@pytest.mark.parametrize("operator", _CoreOperator._member_map_.values())
def test_core_operators_int(
    operator: _CoreOperator,
    field: str,
    int_value: int,
):
    flt = f"{field} {operator.value} {int_value}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert isinstance(resp.value, int)
    assert resp.value == int_value


@pytest.mark.parametrize("operator", _CoreOperator._member_map_.values())
def test_core_operators_float(
    operator: _CoreOperator,
    field: str,
    float_value: float,
):
    flt = f"{field} {operator.value} {float_value}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert isinstance(resp.value, float)
    assert resp.value == float_value


@pytest.mark.parametrize("operator", _CoreOperator._member_map_.values())
def test_core_operators_string(
    operator: _CoreOperator,
    field: str,
    str_value: str,
):
    flt = f"{field} {operator.value} {str_value!r}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, TextFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert isinstance(resp.value, str)
    assert resp.value == str_value


@pytest.mark.parametrize("operator", _CoreOperator._member_map_.values())
def test_core_operators_datetime(
    operator: _CoreOperator,
    field: str,
    datetime_value: str,
):
    flt = f"{field} {operator.value} {datetime_value!r}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, DateTimeFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert isinstance(resp.value, datetime)


@pytest.mark.parametrize("operator", _InOperator._member_map_.values())
def test_in_operators_numbers(
    operator: _InOperator, field: str, int_values: Sequence[int]
):
    flt = f"{field} {operator.value} ({','.join(map(str, int_values))})"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, int)
        assert v in int_values


@pytest.mark.parametrize("operator", _InOperator._member_map_.values())
def test_in_operators_strings(operator: _InOperator):
    field = "REF_AREA"
    values = ["AR", "UY"]
    values_str = [f"{i!r}" for i in values]
    flt = f"{field} {operator.value} ({','.join(values_str)})"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, TextFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, str)
        assert v in values


@pytest.mark.parametrize("operator", _InOperator._member_map_.values())
def test_in_operators_lower(
    operator: _InOperator, field: str, int_values: Sequence[int]
):
    op = operator.value.lower()
    flt = f"{field} {op} ({','.join(map(str, int_values))})"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, int)
        assert v in int_values


@pytest.mark.parametrize("operator", _RangeOperator._member_map_.values())
def test_range_operators(
    operator: _RangeOperator, field: str, int_values: Sequence[int]
):
    flt = f"{field} {operator.value} {int_values[0]} AND {int_values[1]}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, int)
        assert v in int_values


@pytest.mark.parametrize("operator", _RangeOperator._member_map_.values())
def test_range_operators_date_time(
    operator: _RangeOperator, field: str, datetime_values: Sequence[int]
):
    op = operator.value.lower()
    flt = f"{field} {op} {datetime_values[0]!r} AND {datetime_values[1]!r}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, DateTimeFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, datetime)
        assert v.year == 2024
        assert v.month == 5
        assert v.day in [1, 23]


@pytest.mark.parametrize("operator", _RangeOperator._member_map_.values())
def test_range_operators_lower(
    operator: _RangeOperator, field: str, int_values: Sequence[int]
):
    op = operator.value.lower()
    flt = f"{field} {op} {int_values[0]} AND {int_values[1]}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, int)
        assert v in int_values


def test_string_value():
    field = "REF_AREA"
    operator = _CoreOperator.EQUALS
    value = "AR"
    flt = f"{field} {operator.value} {value!r}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, TextFilter)
    assert resp.field == field
    assert resp.operator == Operator[operator.name]
    assert isinstance(resp.value, str)
    assert resp.value == value


def test_multiple_filters():
    fld1 = "REF_AREA"
    op1 = _CoreOperator.EQUALS
    val1 = "UY"
    fld2 = "TIME_PERIOD"
    op2 = _CoreOperator.GREATER_THAN_OR_EQUAL
    val2 = "2020-01-01"
    flt = f"{fld1}{op1.value}{val1!r} AND {fld2} {op2.value} {val2!r}"

    resp = sql_parser.parse(flt)

    assert isinstance(resp, MultiFilter)
    assert len(resp.filters) == 2
    assert resp.operator == LogicalOperator.AND
    for rf in resp.filters:
        if rf.field == fld1:
            assert isinstance(rf, TextFilter)
            assert rf.operator == Operator[op1.name]
            assert rf.value == val1
        else:
            assert isinstance(rf, DateTimeFilter)
            assert rf.field == fld2
            assert rf.operator == Operator[op2.name]
            assert rf.value.year == 2020
            assert rf.value.month == 1
            assert rf.value.day == 1
            assert rf.value.hour == 0
            assert rf.value.minute == 0
            assert rf.value.second == 0
            assert rf.value.microsecond == 0
            assert rf.value.tzinfo == timezone.utc
