import pytest

from pysdmx.model import Component, Concept, DataType, Facets, Role
from pysdmx.toolkit.sqlsrv import get_sql_data_type


@pytest.mark.parametrize(
    ("data_type", "expected_sql_type"),
    [
        (DataType.SHORT, "SMALLINT"),
        (DataType.INTEGER, "INT"),
        (DataType.LONG, "BIGINT"),
        (DataType.COUNT, "BIGINT"),
        (DataType.BIG_INTEGER, "DECIMAL(38, 0)"),
        (DataType.DECIMAL, "DECIMAL(38, 18)"),
        (DataType.FLOAT, "REAL"),
        (DataType.DOUBLE, "FLOAT"),
    ],
)
def test_numeric_type_mapping(data_type, expected_sql_type):
    """Test mapping of various numeric data types."""
    cmp = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        data_type,
        attachment_level="O",
    )
    assert get_sql_data_type(cmp) == expected_sql_type


@pytest.mark.parametrize(
    ("data_type", "expected_sql_type"),
    [
        (DataType.YEAR, "VARCHAR(10)"),
        (DataType.MONTH, "VARCHAR(10)"),
        (DataType.DAY, "VARCHAR(11)"),
        (DataType.YEAR_MONTH, "VARCHAR(13)"),
        (DataType.MONTH_DAY, "VARCHAR(13)"),
        (DataType.REP_YEAR, "CHAR(7)"),
        (DataType.REP_SEMESTER, "CHAR(7)"),
        (DataType.REP_TRIMESTER, "CHAR(7)"),
        (DataType.REP_QUARTER, "CHAR(7)"),
        (DataType.REP_MONTH, "CHAR(8)"),
        (DataType.REP_WEEK, "CHAR(8)"),
        (DataType.REP_DAY, "CHAR(9)"),
        (DataType.GREGORIAN_TIME_PERIOD, "VARCHAR(16)"),
        (DataType.STD_TIME_PERIOD, "VARCHAR(50)"),
        (DataType.BASIC_TIME_PERIOD, "VARCHAR(25)"),
        (DataType.PERIOD, "VARCHAR(50)"),
        (DataType.DURATION, "VARCHAR(50)"),
        (DataType.DATE_TIME, "DATETIME2"),
        (DataType.DATE, "DATE"),
        (DataType.TIME, "TIME"),
    ],
)
def test_date_time_type_mapping(data_type, expected_sql_type):
    """Test mapping of various date and time data types."""
    cmp = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        data_type,
        attachment_level="O",
    )
    assert get_sql_data_type(cmp) == expected_sql_type


def test_boolean_type_mapping():
    """Test mapping of boolean data types."""
    cmp = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        DataType.BOOLEAN,
        attachment_level="O",
    )
    assert get_sql_data_type(cmp) == "BIT"


def test_incremental_type_mapping():
    """Test mapping of incremental data types."""
    cmp = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        DataType.INCREMENTAL,
        Facets(is_sequence=True, interval=1),
        attachment_level="O",
    )
    assert get_sql_data_type(cmp) == "INT"


@pytest.mark.parametrize(
    "data_type",
    [
        DataType.ALPHA,
        DataType.ALPHA_NUM,
        DataType.NUMERIC,
        DataType.STRING,
        DataType.URI,
        DataType.XHTML,
    ],
)
def test_string_type_mapping(data_type):
    """Test mapping of miscellaneous data types."""
    cmp = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        data_type,
        attachment_level="O",
    )
    assert (
        get_sql_data_type(cmp) == "VARCHAR(MAX)"
        if data_type == DataType.NUMERIC
        else "NVARCHAR(MAX)"
    )


@pytest.mark.parametrize(
    ("facets", "expected_sql_type"),
    [
        (Facets(min_length=5, max_length=5), "CHAR(5)"),
        (Facets(max_length=255), "NVARCHAR(255)"),
        (None, "NVARCHAR(MAX)"),
    ],
)
def test_facet_handling(facets, expected_sql_type):
    """Test handling of facets for CHAR and NVARCHAR types."""
    cmp = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        DataType.STRING,
        facets,
        attachment_level="O",
    )
    assert get_sql_data_type(cmp) == expected_sql_type
