import re
from datetime import datetime, timezone
from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io.json.sdmxjson2.reader.doc_validation import validate_sdmx_json
from pysdmx.io.json.sdmxjson2.reader.metadata import read as read_metadata
from pysdmx.io.json.sdmxjson2.reader.structure import read as read_structure


@pytest.fixture
def agency_id_missing():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "agency_id_missing.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def invalid_pattern():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "invalid_pattern.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def unexpected_property():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "unexpected_property.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def invalid_type():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "invalid_type.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def invalid_value():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "invalid_value.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def empty_group_dimensions():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "empty_group_dimensions.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def valid_metadata_21():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "valid_metadata_21.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


def test_json_agency_id_missing(agency_id_missing):
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Validation Error: $.data.metadataSets.0:"
            " missing property 'agencyID'"
        ),
    ):
        read_metadata(agency_id_missing)


def test_json_invalid_pattern(invalid_pattern):
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Validation Error: $.data.metadataSets.0.version:"
            " does not match required pattern"
        ),
    ):
        read_metadata(invalid_pattern)


def test_json_additional_property(unexpected_property):
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Validation Error: $.data.metadataSets.0: unexpected property"
            " 'unexpected property'"
        ),
    ):
        read_metadata(unexpected_property)


def test_invalid_type(invalid_type):
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Validation Error: $.data.dataStructures.0.isExternalReference:"
            " invalid type (expected boolean)"
        ),
    ):
        read_structure(invalid_type)


def test_invalid_value(invalid_value):
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Validation Error: $.data.dataStructures.0.dataStructureComponents"
            ".dimensionList.timeDimension.localRepresentation.format.dataType:"
            " invalid value 'wrongtype' (expected one of:"
            " ObservationalTimePeriod, StandardTimePeriod, BasicTimePeriod,"
            " GregorianTimePeriod, GregorianYear, GregorianYearMonth,"
            " GregorianDay, ReportingTimePeriod, ReportingYear,"
            " ReportingSemester, ReportingTrimester, ReportingQuarter,"
            " ReportingMonth, ReportingWeek, ReportingDay, DateTime,"
            " TimeRange)"
        ),
    ):
        read_structure(invalid_value)


def test_empty_group_dimensions(empty_group_dimensions):
    with pytest.raises(
        Invalid,
        match=re.escape(
            "Validation Error: $.data.dataStructures.0.dataStructureComponents"
            ".groups.0.groupDimensions: [] should be non-empty"
        ),
    ):
        read_structure(empty_group_dimensions)


def test_json_21_metadata_valid(valid_metadata_21):
    # ``isPartialLanguage`` is an SDMX-JSON 2.1-only field: this message is
    # rejected by the 2.0 metadata schema but valid under 2.1. Reading it
    # with validation enabled only succeeds if the reader selected the 2.1
    # schema, which pins the version-aware schema wiring.
    msg = read_metadata(valid_metadata_21, validate=True)

    assert len(msg.reports) == 3


@pytest.fixture
def tzless_datetime():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "tzless_datetime.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def tzless_datetime_and_invalid_type():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "tzless_datetime_and_invalid_type.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def date_prepared_21():
    file_path = (
        Path(__file__).parent
        / "samples"
        / "schema_validations"
        / "date_prepared_21.json"
    )
    with open(file_path, "r") as f:
        text = f.read()
    return text


def test_tzless_datetime_warns_and_reads(tzless_datetime):
    # Datetimes without timezone are allowed by SDMX but are not RFC 3339
    # compliant: the schema failures are reported as a UserWarning and the
    # message is read anyway, with datetimes normalized to UTC.
    with pytest.warns(UserWarning, match="not an RFC 3339 date-time"):
        msg = read_structure(tzless_datetime)

    facets = msg.structures[0].items[0].facets
    assert facets.start_time == datetime(2000, 1, 1, tzinfo=timezone.utc)
    assert facets.end_time == datetime(
        2020, 12, 31, 23, 59, 59, tzinfo=timezone.utc
    )


def test_tzless_datetime_warning_points_at_offending_values(tzless_datetime):
    with pytest.warns(
        UserWarning, match="not an RFC 3339 date-time"
    ) as record:
        read_structure(tzless_datetime)

    assert len(record) == 1
    message = str(record[0].message)
    assert (
        "$.data.conceptSchemes.0.concepts.0.coreRepresentation"
        ".format.startTime: '2000-01-01T00:00:00'"
    ) in message
    assert "$.data.conceptSchemes.0.validFrom: '2003-01-01T00:00:00'" in (
        message
    )


def test_tzless_datetime_with_other_error_still_fails(
    tzless_datetime_and_invalid_type,
):
    with (
        pytest.warns(UserWarning, match="not an RFC 3339 date-time"),
        pytest.raises(
            Invalid,
            match=re.escape(
                "$.data.conceptSchemes.0.isExternalReference:"
                " invalid type (expected boolean)"
            ),
        ),
    ):
        read_structure(tzless_datetime_and_invalid_type)


def test_json_21_date_only_prepared_valid(date_prepared_21, recwarn):
    # Before the strict date-time format check, a date-only ``prepared``
    # matched both the ``date`` and the (unchecked) ``date-time`` branches
    # of the 2.1 ``oneOf``, so it was falsely rejected.
    validate_sdmx_json(date_prepared_21)

    assert len(recwarn) == 0
