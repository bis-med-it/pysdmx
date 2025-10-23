import re
from pathlib import Path

import pytest

from pysdmx.errors import Invalid
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
