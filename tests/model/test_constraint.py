"""Unit tests for the SDMX data constraint model."""

from datetime import datetime

import pytest

from pysdmx.errors import Invalid
from pysdmx.model import (
    AvailabilityConstraint,
    ConstraintAttachment,
    CubeKeyValue,
    CubeRegion,
    CubeTimeRange,
    CubeValue,
    TimePeriodBoundary,
)


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


def test_cube_time_range_valid_shapes():
    before = CubeTimeRange(before_period=TimePeriodBoundary(period="2020"))
    after = CubeTimeRange(after_period=TimePeriodBoundary(period="2020"))
    rng = CubeTimeRange(
        start_period=TimePeriodBoundary(period="2020"),
        end_period=TimePeriodBoundary(period="2024"),
    )
    assert before.before_period.period == "2020"
    assert after.after_period.period == "2020"
    assert rng.start_period.period == "2020"
    assert rng.end_period.period == "2024"


@pytest.mark.parametrize(
    "boundaries",
    [
        {},
        {"start_period": TimePeriodBoundary(period="2020")},
        {"end_period": TimePeriodBoundary(period="2024")},
        {
            "before_period": TimePeriodBoundary(period="2020"),
            "after_period": TimePeriodBoundary(period="2024"),
        },
        {
            "before_period": TimePeriodBoundary(period="2020"),
            "start_period": TimePeriodBoundary(period="2020"),
        },
        {
            "after_period": TimePeriodBoundary(period="2020"),
            "end_period": TimePeriodBoundary(period="2024"),
        },
        {
            "before_period": TimePeriodBoundary(period="2020"),
            "end_period": TimePeriodBoundary(period="2024"),
        },
        {
            "after_period": TimePeriodBoundary(period="2020"),
            "start_period": TimePeriodBoundary(period="2020"),
        },
    ],
)
def test_cube_time_range_invalid_shapes(boundaries):
    with pytest.raises(Invalid, match="time range"):
        CubeTimeRange(**boundaries)


def test_cube_key_value_values_and_time_range_are_exclusive():
    tr = CubeTimeRange(
        start_period=TimePeriodBoundary(period="2020", is_inclusive=True),
        end_period=TimePeriodBoundary(period="2024", is_inclusive=False),
    )
    with pytest.raises(Invalid, match="mutually exclusive"):
        CubeKeyValue(
            id="TIME_PERIOD",
            values=[CubeValue(value="A")],
            time_range=tr,
        )


def test_cube_key_value_keyvalue_validity():
    kv = CubeKeyValue(
        id="FREQ",
        values=[CubeValue(value="A")],
        valid_from=datetime(2020, 1, 1),
        valid_to=datetime(2021, 1, 1),
    )
    assert kv.valid_from == datetime(2020, 1, 1)
    assert kv.values[0].value == "A"


def _attachment(**kwargs):
    defaults = {"data_provider": None}
    defaults.update(kwargs)
    return ConstraintAttachment(**defaults)


DF_URN = (
    "urn:sdmx:org.sdmx.infomodel.datastructure."
    "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
)


def test_availability_constraint():
    region = CubeRegion(
        key_values=[CubeKeyValue(id="FREQ", values=[CubeValue(value="A")])]
    )
    ac = AvailabilityConstraint(
        constraint_attachment=_attachment(dataflows=[DF_URN]),
        cube_region=region,
        series_count=5,
        obs_count=100,
    )
    assert ac.cube_region == region
    assert ac.series_count == 5
    assert ac.obs_count == 100
    assert ac.reference == DF_URN
    assert ac.short_urn == f"AvailabilityConstraint={DF_URN}"
    assert ac.annotations == ()


def test_availability_constraint_counts_default_to_none():
    ac = AvailabilityConstraint(
        constraint_attachment=_attachment(dataflows=[DF_URN]),
        cube_region=CubeRegion(key_values=[]),
    )
    assert ac.series_count is None
    assert ac.obs_count is None


@pytest.mark.parametrize(
    "attachment",
    [
        ConstraintAttachment(data_provider=None),
        ConstraintAttachment(data_provider="DP"),
        ConstraintAttachment(data_provider=None, dataflows=["urn:1", "urn:2"]),
        ConstraintAttachment(
            data_provider=None,
            dataflows=["urn:1"],
            data_structures=["urn:2"],
        ),
        ConstraintAttachment(data_provider="DP", dataflows=["urn:1"]),
    ],
)
def test_availability_constraint_requires_single_data_ref(attachment):
    with pytest.raises(Invalid, match="exactly one"):
        AvailabilityConstraint(
            constraint_attachment=attachment,
            cube_region=CubeRegion(key_values=[]),
        )


@pytest.mark.parametrize("field", ["data_structures", "provision_agreements"])
def test_availability_constraint_accepts_each_ref_kind(field):
    ac = AvailabilityConstraint(
        constraint_attachment=_attachment(**{field: ["urn:x"]}),
        cube_region=CubeRegion(key_values=[]),
    )
    assert ac.reference == "urn:x"
