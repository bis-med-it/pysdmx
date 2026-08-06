"""Unit tests for the SDMX data constraint model."""

from datetime import datetime

from pysdmx.model import (
    ConstraintRole,
    CubeKeyValue,
    CubeTimeRange,
    CubeValue,
    DataConstraint,
    TimePeriodBoundary,
)


def test_data_constraint_role_defaults_to_allowed():
    dc = DataConstraint(id="C1", agency="AG")
    assert dc.role == ConstraintRole.ALLOWED


def test_data_constraint_role_actual():
    dc = DataConstraint(id="C1", agency="AG", role=ConstraintRole.ACTUAL)
    assert dc.role is ConstraintRole.ACTUAL


def test_constraint_role_values_match_sdmx():
    assert ConstraintRole.ALLOWED.value == "Allowed"
    assert ConstraintRole.ACTUAL.value == "Actual"
    assert ConstraintRole("Actual") is ConstraintRole.ACTUAL


def test_constraint_role_str_and_repr():
    assert str(ConstraintRole.ALLOWED) == "Allowed"
    assert str(ConstraintRole.ACTUAL) == "Actual"
    assert repr(ConstraintRole.ACTUAL) == "ConstraintRole.ACTUAL"


def test_cube_key_value_defaults():
    kv = CubeKeyValue(id="FREQ")
    assert kv.values == ()
    assert kv.time_range is None
    assert kv.valid_from is None
    assert kv.valid_to is None


def test_cube_key_value_with_time_range():
    tr = CubeTimeRange(
        start_period=TimePeriodBoundary(period="2020", is_inclusive=True),
        end_period=TimePeriodBoundary(period="2024", is_inclusive=False),
    )
    kv = CubeKeyValue(id="TIME_PERIOD", time_range=tr)
    assert kv.time_range.start_period.period == "2020"
    assert kv.time_range.start_period.is_inclusive is True
    assert kv.time_range.end_period.is_inclusive is False


def test_cube_key_value_keyvalue_validity():
    kv = CubeKeyValue(
        id="FREQ",
        values=[CubeValue(value="A")],
        valid_from=datetime(2020, 1, 1),
        valid_to=datetime(2021, 1, 1),
    )
    assert kv.valid_from == datetime(2020, 1, 1)
    assert kv.values[0].value == "A"
