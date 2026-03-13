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
        (DataType.BIG_INTEGER, "DECIMAL(38, 18)"),
        (DataType.DECIMAL, "DECIMAL(38, 18)"),
        (DataType.FLOAT, "REAL"),
        (DataType.DOUBLE, "FLOAT"),
    ],
)
def test_numeric_type_mapping(data_type, expected_sql_type):
    """Test mapping of various data types."""
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
        (DataType.YEAR, "CHAR(4)"),
        (DataType.MONTH, "TINYINT"),
        (DataType.DAY, "CHAR(5)"),
        (DataType.YEAR_MONTH, "CHAR(7)"),
        (DataType.MONTH_DAY, "CHAR(7)"),
        (DataType.REP_YEAR, "CHAR(7)"),
        (DataType.REP_SEMESTER, "CHAR(7)"),
        (DataType.REP_TRIMESTER, "CHAR(7)"),
        (DataType.REP_QUARTER, "CHAR(7)"),
        (DataType.REP_MONTH, "CHAR(8)"),
        (DataType.REP_WEEK, "CHAR(8)"),
        (DataType.REP_DAY, "CHAR(9)"),
        (DataType.GREGORIAN_TIME_PERIOD, "CHAR(10)"),
        (DataType.STD_TIME_PERIOD, "NVARCHAR(50)"),
        (DataType.BASIC_TIME_PERIOD, "NVARCHAR(25)"),
        (DataType.PERIOD, "NVARCHAR(50)"),
        (DataType.DURATION, "NVARCHAR(50)"),
        (DataType.DATE_TIME, "DATETIME2"),
        (DataType.DATE, "DATE"),
        (DataType.TIME, "TIME"),
    ],
)
def test_date_time_type_mapping(data_type, expected_sql_type):
    """Test mapping of various data types."""
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
    """Test mapping of various data types."""
    cmp = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        DataType.BOOLEAN,
        attachment_level="O",
    )
    assert get_sql_data_type(cmp) == "BIT"


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
    """Test mapping of various data types."""
    cmp = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        data_type,
        attachment_level="O",
    )
    assert get_sql_data_type(cmp) == "NVARCHAR(MAX)"


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
