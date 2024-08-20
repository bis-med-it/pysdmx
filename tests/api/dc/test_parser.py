from datetime import timedelta

import pytest

from pysdmx.api.dc.query import (
    DateTimeFilter,
    LogicalOperator,
    MultiFilter,
    NumberFilter,
    Operator,
    parse_query,
    TextFilter,
)
from pysdmx.errors import Invalid


def test_sql_query():
    qs = (
        "REF_AREA='UY' AND FREQ <> 'A' AND TIME_PERIOD >='2024-01-01' "
        "AND OBS_STATUS IN ('A','F') AND OBS_VALUE = 42 "
        "AND LAST_UPDATED > '2024-01-15T10:42:21+01:00'"
    )

    flts = parse_query(qs)

    assert isinstance(flts, MultiFilter)
    assert len(flts.filters) == 6
    assert flts.operator == LogicalOperator.AND
    for idx, flt in enumerate(flts.filters):
        if idx == 0:
            assert isinstance(flt, TextFilter)
            assert flt.field == "REF_AREA"
            assert flt.operator == Operator.EQUALS
            assert flt.value == "UY"
        elif idx == 1:
            assert isinstance(flt, TextFilter)
            assert flt.field == "FREQ"
            assert flt.operator == Operator.NOT_EQUALS
            assert flt.value == "A"
        elif idx == 2:
            assert isinstance(flt, DateTimeFilter)
            assert flt.field == "TIME_PERIOD"
            assert flt.operator == Operator.GREATER_THAN_OR_EQUAL
            assert flt.value.year == 2024
            assert flt.value.month == 1
            assert flt.value.day == 1
        elif idx == 3:
            assert isinstance(flt, TextFilter)
            assert flt.field == "OBS_STATUS"
            assert flt.operator == Operator.IN
            assert len(flt.value) == 2
            for i in flt.value:
                assert i in ["A", "F"]
        elif idx == 4:
            assert isinstance(flt, NumberFilter)
            assert flt.field == "OBS_VALUE"
            assert flt.operator == Operator.EQUALS
            assert flt.value == 42
        elif idx == 5:
            assert isinstance(flt, DateTimeFilter)
            assert flt.field == "LAST_UPDATED"
            assert flt.operator == Operator.GREATER_THAN
            assert flt.value.year == 2024
            assert flt.value.month == 1
            assert flt.value.day == 15
            assert flt.value.hour == 10
            assert flt.value.minute == 42
            assert flt.value.second == 21
            assert flt.value.microsecond == 0
            assert flt.value.utcoffset() == timedelta(0, 3600)


def test_py_query():
    qs = (
        "REF_AREA=='UY' and FREQ != 'A' and TIME_PERIOD >='2024-01-01' "
        "and OBS_STATUS in ['A','F'] and OBS_VALUE == 42 "
        "and LAST_UPDATED > '2024-01-15T10:42:21+01:00'"
    )

    flts = parse_query(qs)

    assert isinstance(flts, MultiFilter)
    assert len(flts.filters) == 6
    assert flts.operator == LogicalOperator.AND
    for idx, flt in enumerate(flts.filters):
        if idx == 0:
            assert isinstance(flt, TextFilter)
            assert flt.field == "REF_AREA"
            assert flt.operator == Operator.EQUALS
            assert flt.value == "UY"
        elif idx == 1:
            assert isinstance(flt, TextFilter)
            assert flt.field == "FREQ"
            assert flt.operator == Operator.NOT_EQUALS
            assert flt.value == "A"
        elif idx == 2:
            assert isinstance(flt, DateTimeFilter)
            assert flt.field == "TIME_PERIOD"
            assert flt.operator == Operator.GREATER_THAN_OR_EQUAL
            assert flt.value.year == 2024
            assert flt.value.month == 1
            assert flt.value.day == 1
        elif idx == 3:
            assert isinstance(flt, TextFilter)
            assert flt.field == "OBS_STATUS"
            assert flt.operator == Operator.IN
            assert len(flt.value) == 2
            for i in flt.value:
                assert i in ["A", "F"]
        elif idx == 4:
            assert isinstance(flt, NumberFilter)
            assert flt.field == "OBS_VALUE"
            assert flt.operator == Operator.EQUALS
            assert flt.value == 42
        elif idx == 5:
            assert isinstance(flt, DateTimeFilter)
            assert flt.field == "LAST_UPDATED"
            assert flt.operator == Operator.GREATER_THAN
            assert flt.value.year == 2024
            assert flt.value.month == 1
            assert flt.value.day == 15
            assert flt.value.hour == 10
            assert flt.value.minute == 42
            assert flt.value.second == 21
            assert flt.value.microsecond == 0
            assert flt.value.utcoffset() == timedelta(0, 3600)


def test_parse_error():
    with pytest.raises(Invalid) as e:
        parse_query("blah")
    assert e.value.title == "Unparseable query"
    assert "blah" in e.value.description
