from datetime import datetime

import msgspec
import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.constraint import (
    JsonAvailabilityConstraint,
    JsonDataConstraint,
)
from pysdmx.model import (
    Annotation,
    AvailabilityConstraint,
    ConstraintAttachment,
    CubeKeyValue,
    CubeRegion,
    CubeTimeRange,
    CubeValue,
    DataConstraint,
    TimePeriodBoundary,
)


def _make_data_constraint():
    return DataConstraint(
        id="CONS",
        name="Constraint",
        agency="TEST_AGENCY",
        version="1.0",
        # JsonDataConstraint.from_model requires a constraint
        # attachment (pre-existing validation, unrelated to this
        # task); mirror the other fixtures in this module.
        constraint_attachment=ConstraintAttachment(data_provider="5B0"),
    )


def _make_availability():
    return AvailabilityConstraint(
        constraint_attachment=ConstraintAttachment(
            data_provider=None,
            dataflows=[
                "urn:sdmx:org.sdmx.infomodel.datastructure."
                "Dataflow=TEST_AGENCY:DF_TEST(1.0)"
            ],
        ),
        cube_region=CubeRegion(
            key_values=[
                # A tuple here, not a list: JsonKeyValue.to_model()
                # always rebuilds `values` as a tuple, so the round
                # trip in test_availability_constraint_native_roundtrip
                # must start from the same container type for msgspec
                # struct equality to hold.
                CubeKeyValue(id="FREQ", values=(CubeValue(value="M"),))
            ]
        ),
        series_count=3,
        obs_count=42,
    )


@pytest.fixture
def constraint_no_name():
    return DataConstraint(
        "TEST",
        agency="BIS",
        constraint_attachment=ConstraintAttachment(data_provider="5B0"),
    )


@pytest.fixture
def constraint_no_attachment():
    return DataConstraint("TEST", agency="BIS", name="Test")


def test_constraint_no_name(constraint_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonDataConstraint.from_model(constraint_no_name)


def test_constraint_no_attachment(constraint_no_attachment):
    with pytest.raises(
        errors.Invalid, match="must have a constraint attachment"
    ):
        JsonDataConstraint.from_model(constraint_no_attachment)


@pytest.fixture
def constraint_time_range():
    return DataConstraint(
        "TEST",
        agency="BIS",
        name="Test",
        constraint_attachment=ConstraintAttachment(data_provider="5B0"),
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="TIME_PERIOD",
                        time_range=CubeTimeRange(
                            start_period=TimePeriodBoundary("2020", True),
                            end_period=TimePeriodBoundary("2024", False),
                        ),
                    )
                ]
            )
        ],
    )


def test_constraint_time_range_round_trip(constraint_time_range):
    sjson = JsonDataConstraint.from_model(constraint_time_range)
    key_value = sjson.cubeRegions[0].keyValues[0]

    # A time-range key value must not also carry values.
    assert len(key_value.values) == 0
    assert key_value.timeRange is not None

    encoded = msgspec.json.encode(sjson)
    assert b'"timeRange"' in encoded
    # msgspec omits the empty ``values`` on newer versions but emits
    # ``"values":[]`` on the msgspec that ships for Python 3.10; either way
    # it must never carry populated values alongside a time range.
    assert b'"values":[{' not in encoded

    back = msgspec.json.Decoder(JsonDataConstraint).decode(encoded)
    constraint = back.to_model()

    kv = constraint.cube_regions[0].key_values[0]
    assert kv.time_range.start_period.period == "2020"
    assert kv.time_range.start_period.is_inclusive is True
    assert kv.time_range.end_period.period == "2024"
    assert kv.time_range.end_period.is_inclusive is False
    assert len(kv.values) == 0


@pytest.fixture
def constraint_key_value_validity():
    return DataConstraint(
        "TEST",
        agency="BIS",
        name="Test",
        constraint_attachment=ConstraintAttachment(data_provider="5B0"),
        cube_regions=[
            CubeRegion(
                key_values=[
                    CubeKeyValue(
                        id="FREQ",
                        values=[CubeValue("A")],
                        valid_from=datetime(2020, 1, 1),
                        valid_to=datetime(2024, 1, 1),
                    )
                ]
            )
        ],
    )


def test_constraint_key_value_validity_round_trip(
    constraint_key_value_validity,
):
    sjson = JsonDataConstraint.from_model(constraint_key_value_validity)
    key_value = sjson.cubeRegions[0].keyValues[0]

    # A plain values key value must not also carry a time range.
    assert len(key_value.values) == 1
    assert key_value.timeRange is None

    encoded = msgspec.json.encode(sjson)
    assert b'"timeRange"' not in encoded
    assert b'"validFrom":"2020-01-01T00:00:00"' in encoded
    assert b'"validTo":"2024-01-01T00:00:00"' in encoded

    back = msgspec.json.Decoder(JsonDataConstraint).decode(encoded)
    constraint = back.to_model()

    kv = constraint.cube_regions[0].key_values[0]
    assert kv.time_range is None
    assert len(kv.values) == 1
    assert kv.values[0].value == "A"
    assert kv.valid_from == datetime(2020, 1, 1)
    assert kv.valid_to == datetime(2024, 1, 1)


def test_data_constraint_ser_has_allowed_role():
    ser = JsonDataConstraint.from_model(_make_data_constraint())
    assert ser.role == "Allowed"


def test_data_constraint_ser_without_role_for_2_1():
    ser = JsonDataConstraint.from_model(
        _make_data_constraint(), with_role=False
    )
    assert ser.role is None


def test_availability_as_legacy_data_constraint():
    ser = JsonDataConstraint.from_availability(_make_availability())
    assert ser.role == "Actual"
    assert ser.id == "DF_TEST"
    assert ser.agency == "TEST_AGENCY"
    assert ser.name == "Availability for DF_TEST"


def test_availability_as_legacy_data_constraint_without_counts():
    ac = msgspec.structs.replace(
        _make_availability(), series_count=None, obs_count=None
    )
    ser = JsonDataConstraint.from_availability(ac)
    assert ser.annotations == ()


def test_availability_as_legacy_data_constraint_keeps_annotations():
    # Parity with the SDMX-ML 2.1/3.0 twin
    # (__availability_as_data_constraint), which already passes
    # annotations through, then appends the counts as FMR-style
    # sdmx_metrics annotations (own annotations first).
    ac = msgspec.structs.replace(
        _make_availability(), annotations=(Annotation(id="ANN1"),)
    )
    ser = JsonDataConstraint.from_availability(ac)
    assert len(ser.annotations) == 3
    assert ser.annotations[0].id == "ANN1"
    assert ser.annotations[1].id == "series_count"
    assert ser.annotations[1].type == "sdmx_metrics"
    assert ser.annotations[1].title == "3"
    assert ser.annotations[2].id == "obs_count"
    assert ser.annotations[2].type == "sdmx_metrics"
    assert ser.annotations[2].title == "42"


def test_availability_constraint_native_roundtrip():
    ac = _make_availability()
    ser = JsonAvailabilityConstraint.from_model(ac)
    assert ser.seriesCount == ac.series_count
    assert ser.to_model() == ac


def test_availability_constraint_native_requires_attachment_and_region():
    with pytest.raises(errors.Invalid, match="cube region"):
        JsonAvailabilityConstraint().to_model()
