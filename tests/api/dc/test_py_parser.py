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
from pysdmx.api.dc.query._py_parser import (
    PythonOperator,
    _PythonCoreOperator,
    _PythonInOperator,
    _to_operator,
    py_parser,
)


@pytest.fixture
def field() -> str:
    return "OBS_VALUE"


@pytest.fixture
def int_value() -> int:
    return 42


@pytest.fixture
def float_value() -> float:
    return 42.84


@pytest.fixture
def str_value() -> str:
    return "A"


@pytest.fixture
def int_values() -> Sequence[int]:
    return [42, 83]


def test_eq_operator():
    op = _to_operator(PythonOperator.EQUALS)

    assert op == Operator.EQUALS


def test_ne_operator():
    op = _to_operator(PythonOperator.NOT_EQUALS)

    assert op == Operator.NOT_EQUALS


def test_lt_operator():
    op = _to_operator(PythonOperator.LESS_THAN)

    assert op == Operator.LESS_THAN


def test_le_operator():
    op = _to_operator(PythonOperator.LESS_THAN_OR_EQUAL)

    assert op == Operator.LESS_THAN_OR_EQUAL


def test_gt_operator():
    op = _to_operator(PythonOperator.GREATER_THAN)

    assert op == Operator.GREATER_THAN


def test_ge_operator():
    op = _to_operator(PythonOperator.GREATER_THAN_OR_EQUAL)

    assert op == Operator.GREATER_THAN_OR_EQUAL


def test_in_operator():
    op = _to_operator(PythonOperator.IN)

    assert op == Operator.IN


def test_ni_operator():
    op = _to_operator(PythonOperator.NOT_IN)

    assert op == Operator.NOT_IN


@pytest.mark.parametrize("operator", _PythonCoreOperator._member_map_.values())
def test_core_operators_int(
    operator: _PythonCoreOperator,
    field: str,
    int_value: int,
):
    flt = f"{field} {operator.value} {int_value}"

    resp = py_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == _to_operator(operator)
    assert isinstance(resp.value, int)
    assert resp.value == int_value


@pytest.mark.parametrize("operator", _PythonCoreOperator._member_map_.values())
def test_core_operators_float(
    operator: _PythonCoreOperator,
    field: str,
    float_value: float,
):
    flt = f"{field} {operator.value} {float_value}"

    resp = py_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == _to_operator(operator)
    assert isinstance(resp.value, float)
    assert resp.value == float_value


@pytest.mark.parametrize("operator", _PythonCoreOperator._member_map_.values())
def test_core_operators_string(
    operator: _PythonCoreOperator,
    field: str,
    str_value: str,
):
    flt = f"{field} {operator.value} {str_value!r}"

    resp = py_parser.parse(flt)

    assert isinstance(resp, TextFilter)
    assert resp.field == field
    assert resp.operator == _to_operator(operator)
    assert isinstance(resp.value, str)
    assert resp.value == str_value


@pytest.mark.parametrize("operator", _PythonInOperator._member_map_.values())
def test_in_operators_numbers(
    operator: _PythonInOperator, field: str, int_values: Sequence[int]
):
    flt = f"{field} {operator.value} ({','.join(map(str, int_values))})"

    resp = py_parser.parse(flt)

    assert isinstance(resp, NumberFilter)
    assert resp.field == field
    assert resp.operator == _to_operator(operator)
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, int)
        assert v in int_values


@pytest.mark.parametrize("operator", _PythonInOperator._member_map_.values())
def test_in_operators_strings(operator: _PythonInOperator):
    field = "REF_AREA"
    values = ["AR", "UY"]
    values_str = [f"{i!r}" for i in values]
    flt = f"{field} {operator.value} ({','.join(values_str)})"

    resp = py_parser.parse(flt)

    assert isinstance(resp, TextFilter)
    assert resp.field == field
    assert resp.operator == _to_operator(operator)
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, str)
        assert v in values


@pytest.mark.parametrize("operator", _PythonInOperator._member_map_.values())
def test_in_operators_strings_list(operator: _PythonInOperator):
    field = "REF_AREA"
    values = ["AR", "UY"]
    values_str = [f"{i!r}" for i in values]
    flt = f"{field} {operator.value} [{','.join(values_str)}]"

    resp = py_parser.parse(flt)

    assert isinstance(resp, TextFilter)
    assert resp.field == field
    assert resp.operator == _to_operator(operator)
    assert len(resp.value) == 2
    for v in resp.value:
        assert isinstance(v, str)
        assert v in values


def test_string_value():
    field = "REF_AREA"
    operator = _PythonCoreOperator.EQUALS
    value = "AR"
    flt = f"{field} {operator.value} {value!r}"

    resp = py_parser.parse(flt)

    assert isinstance(resp, TextFilter)
    assert resp.field == field
    assert resp.operator == Operator.EQUALS
    assert isinstance(resp.value, str)
    assert resp.value == value


def test_multiple_filters():
    fld1 = "REF_AREA"
    op1 = _PythonCoreOperator.EQUALS
    val1 = "UY"
    fld2 = "LAST_UPDATED"
    op2 = _PythonCoreOperator.GREATER_THAN_OR_EQUAL
    val2 = "2020-01-01T23:42:59.420+00:00"
    flt = f"{fld1}{op1.value}{val1!r} and {fld2} {op2.value} {val2!r}"

    resp = py_parser.parse(flt)
    assert isinstance(resp, MultiFilter)
    assert resp.operator == LogicalOperator.AND
    assert len(resp.filters) == 2
    for rf in resp.filters:
        if rf.field == fld1:
            assert isinstance(rf, TextFilter)
            assert rf.operator == Operator.EQUALS
            assert rf.value == val1
        else:
            assert isinstance(rf, DateTimeFilter)
            assert rf.field == fld2
            assert rf.operator == Operator.GREATER_THAN_OR_EQUAL
            assert rf.value.year == 2020
            assert rf.value.month == 1
            assert rf.value.day == 1
            assert rf.value.hour == 23
            assert rf.value.minute == 42
            assert rf.value.second == 59
            assert rf.value.microsecond == 420000
            assert rf.value.tzinfo == timezone.utc


@pytest.mark.parametrize(
    "value",
    [
        "2020-01-01",  # Daily or Business frequency
        "2020-W01",  # Weekly frequency
        "2020-01",  # Monthly frequency
        "2020-Q1",  # Quarterly frequency
        "2020-S1",  # Semi-annual frequency
        "2020-H1",  # Semi-annual frequency (old code)
        "2020",  # Annual frequency
    ],
)
def test_period_formats(value):
    field = "TIME_PERIOD"
    operator = _PythonCoreOperator.GREATER_THAN_OR_EQUAL
    flt = f"{field} {operator.value} {value!r}"

    resp = py_parser.parse(flt)

    assert isinstance(resp, TextFilter)
    assert resp.field == field
    assert resp.operator == Operator.GREATER_THAN_OR_EQUAL
    assert isinstance(resp.value, str)
    assert resp.value == value


@pytest.mark.parametrize(
    "value",
    [
        "2020-01-01T23:42",
        "2020-01-01t23:42",
        "2020-01-01T23:42:59",
        "2020-01-01T23:42:59.420",
        "2020-01-01T23:42:59.123456",
        "2020-01-01T23:42:59.1234567+00:00",
        "2020-01-01T23:42Z",
        "2020-01-01T23:42+00:00",
        "2020-01-01T23:42+0000",
        "2020-01-01T23:42:59.420+01:00",
    ],
)
def test_datetime_formats(value):
    field = "LAST_UPDATED"
    operator = _PythonCoreOperator.GREATER_THAN_OR_EQUAL
    flt = f"{field} {operator.value} {value!r}"

    resp = py_parser.parse(flt)

    assert isinstance(resp, DateTimeFilter)
    assert resp.field == field
    assert resp.operator == Operator.GREATER_THAN_OR_EQUAL
    assert isinstance(resp.value, datetime)
