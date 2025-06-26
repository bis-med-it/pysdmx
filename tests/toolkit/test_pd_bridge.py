import pytest

from pysdmx.model import (
    Code,
    Codelist,
    Component,
    Components,
    Concept,
    DataType,
    Role,
)
from pysdmx.toolkit.pd import to_pandas_schema, to_pandas_type


@pytest.mark.parametrize(
    ("dt", "required", "expected"),
    [
        (DataType.SHORT, True, "int16"),
        (DataType.SHORT, False, "Int16"),
        (DataType.INTEGER, True, "int32"),
        (DataType.INTEGER, False, "Int32"),
        (DataType.LONG, True, "int64"),
        (DataType.LONG, False, "Int64"),
        (DataType.BIG_INTEGER, True, "object"),
        (DataType.BIG_INTEGER, False, "object"),
        (DataType.COUNT, True, "int64"),
        (DataType.COUNT, False, "Int64"),
    ],
)
def test_whole_numbers(dt: DataType, required: bool, expected: str):
    comp = Component(
        "TEST",
        required,
        Role.ATTRIBUTE,
        Concept("TEST"),
        dt,
        attachment_level="D",
    )

    received = to_pandas_type(comp)

    assert received == expected


@pytest.mark.parametrize(
    ("dt", "required", "expected"),
    [
        (DataType.FLOAT, True, "float32"),
        (DataType.FLOAT, False, "Float32"),
        (DataType.DOUBLE, True, "float64"),
        (DataType.DOUBLE, False, "Float64"),
        (DataType.DECIMAL, True, "object"),
        (DataType.DECIMAL, False, "object"),
    ],
)
def test_decimal_numbers(dt: DataType, required: bool, expected: str):
    comp = Component(
        "TEST",
        required,
        Role.ATTRIBUTE,
        Concept("TEST"),
        dt,
        attachment_level="D",
    )

    received = to_pandas_type(comp)

    assert received == expected


@pytest.mark.parametrize(
    ("dt", "required", "expected"),
    [
        (DataType.DATE_TIME, True, "datetime64[ns]"),
        (DataType.DATE_TIME, False, "datetime64[ns]"),
        (DataType.DATE, True, "datetime64[D]"),
        (DataType.DATE, False, "datetime64[D]"),
        (DataType.YEAR_MONTH, True, "datetime64[M]"),
        (DataType.YEAR_MONTH, False, "datetime64[M]"),
        (DataType.YEAR, True, "datetime64[Y]"),
        (DataType.YEAR, False, "datetime64[Y]"),
        (DataType.GREGORIAN_TIME_PERIOD, True, "object"),
        (DataType.GREGORIAN_TIME_PERIOD, False, "object"),
        (DataType.MONTH, True, "int8"),
        (DataType.MONTH, False, "Int8"),
    ],
)
def test_dates(dt: DataType, required: bool, expected: str):
    comp = Component(
        "TEST",
        required,
        Role.ATTRIBUTE,
        Concept("TEST"),
        dt,
        attachment_level="D",
    )

    received = to_pandas_type(comp)

    assert received == expected


@pytest.mark.parametrize(
    ("dt", "required", "expected"),
    [
        (DataType.BOOLEAN, True, "bool"),
        (DataType.BOOLEAN, False, "boolean"),
    ],
)
def test_booleans(dt: DataType, required: bool, expected: str):
    comp = Component(
        "TEST",
        required,
        Role.ATTRIBUTE,
        Concept("TEST"),
        dt,
        attachment_level="D",
    )

    received = to_pandas_type(comp)

    assert received == expected


@pytest.mark.parametrize(
    "dt",
    [
        DataType.ALPHA,
        DataType.ALPHA_NUM,
        DataType.BASIC_TIME_PERIOD,
        DataType.DAY,
        DataType.DURATION,
        DataType.MONTH_DAY,
        DataType.NUMERIC,
        DataType.PERIOD,
        DataType.REP_DAY,
        DataType.REP_MONTH,
        DataType.REP_QUARTER,
        DataType.REP_SEMESTER,
        DataType.REP_TRIMESTER,
        DataType.REP_WEEK,
        DataType.REP_YEAR,
        DataType.STD_TIME_PERIOD,
        DataType.STRING,
        DataType.TIME,
        DataType.URI,
        DataType.XHTML,
    ],
)
def test_strings(dt: DataType):
    comp = Component(
        "TEST", True, Role.ATTRIBUTE, Concept("TEST"), dt, attachment_level="D"
    )

    received = to_pandas_type(comp)

    assert received == "string"


def test_enumeration():
    comp = Component(
        "TEST",
        True,
        Role.ATTRIBUTE,
        Concept("TEST"),
        DataType.STRING,
        attachment_level="D",
        local_codes=Codelist(
            "CL_FREQ", agency="BIS", items=[Code("A"), Code("M")]
        ),
    )

    received = to_pandas_type(comp)

    assert received == "category"


def test_schema():
    c1 = Component(
        "FREQ",
        True,
        Role.DIMENSION,
        Concept("FREQ"),
        DataType.STRING,
        local_codes=Codelist(
            "CL_FREQ", agency="BIS", items=[Code("A"), Code("M")]
        ),
    )
    c2 = Component(
        "MIC", True, Role.DIMENSION, Concept("MIC"), DataType.STRING
    )
    c3 = Component(
        "TIME_PERIOD",
        True,
        Role.DIMENSION,
        Concept("TIME_PERIOD"),
        DataType.PERIOD,
    )
    c4 = Component(
        "OBS_VALUE",
        True,
        Role.MEASURE,
        Concept("OBS_VALUE"),
        DataType.DOUBLE,
    )
    c5 = Component(
        "OBS_STATUS",
        True,
        Role.ATTRIBUTE,
        Concept("OBS_STATUS"),
        DataType.STRING,
        local_codes=Codelist(
            "CL_OBS_STATUS",
            agency="BIS",
            items=[Code("A"), Code("E"), Code("M")],
        ),
        attachment_level="D"
    )
    exp = {
        "FREQ": "category",
        "MIC": "string",
        "TIME_PERIOD": "string",
        "OBS_VALUE": "float64",
        "OBS_STATUS": "category",
    }

    schema = to_pandas_schema(Components([c1, c2, c3, c4, c5]))

    assert schema == exp
