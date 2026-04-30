import pandas as pd
import pyarrow as pa
import pytest

from pysdmx.model import (
    Code,
    Codelist,
    Component,
    Components,
    Concept,
    DataType,
    Facets,
    Role,
)
from pysdmx.toolkit.pd import to_pyarrow_schema, to_pyarrow_type


@pytest.mark.parametrize(
    ("dt", "expected_pa_type"),
    [
        (DataType.SHORT, pa.int16()),
        (DataType.INTEGER, pa.int32()),
        (DataType.LONG, pa.int64()),
        (DataType.COUNT, pa.int64()),
        (DataType.BIG_INTEGER, pa.string()),
        (DataType.FLOAT, pa.float32()),
        (DataType.DOUBLE, pa.float64()),
        (DataType.DECIMAL, pa.float64()),
        (DataType.BOOLEAN, pa.bool_()),
        (DataType.MONTH, pa.int8()),
        (DataType.DATE, pa.date32()),
        (DataType.DATE_TIME, pa.timestamp("ns")),
    ],
)
def test_typed_components(dt: DataType, expected_pa_type):
    comp = Component(
        "TEST",
        True,
        Role.ATTRIBUTE,
        Concept("TEST"),
        dt,
        attachment_level="D",
    )

    result = to_pyarrow_type(comp)

    assert result == pd.ArrowDtype(expected_pa_type)


@pytest.mark.parametrize(
    "dt",
    [
        DataType.ALPHA,
        DataType.ALPHA_NUM,
        DataType.BASIC_TIME_PERIOD,
        DataType.DAY,
        DataType.DURATION,
        DataType.GREGORIAN_TIME_PERIOD,
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
        DataType.YEAR,
        DataType.YEAR_MONTH,
    ],
)
def test_string_components(dt: DataType):
    comp = Component(
        "TEST",
        True,
        Role.ATTRIBUTE,
        Concept("TEST"),
        dt,
        attachment_level="D",
    )

    result = to_pyarrow_type(comp)

    assert result == pd.ArrowDtype(pa.string())


def test_enumerated_component():
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

    result = to_pyarrow_type(comp)

    assert result == pd.ArrowDtype(pa.string())


@pytest.mark.parametrize(
    ("value", "expected_pa_type"),
    [
        (1, pa.int32()),
        (0.1, pa.float32()),
    ],
)
def test_incremental(value, expected_pa_type):
    comp = Component(
        "TEST",
        True,
        Role.DIMENSION,
        Concept("TEST"),
        DataType.INCREMENTAL,
        Facets(interval=value),
    )

    result = to_pyarrow_type(comp)

    assert result == pd.ArrowDtype(expected_pa_type)


def test_incremental_no_facets():
    comp = Component(
        "TEST",
        True,
        Role.DIMENSION,
        Concept("TEST"),
        DataType.INCREMENTAL,
    )

    result = to_pyarrow_type(comp)

    assert result == pd.ArrowDtype(pa.int32())


def test_required_does_not_affect_pyarrow_type():
    comp_req = Component(
        "TEST",
        True,
        Role.ATTRIBUTE,
        Concept("TEST"),
        DataType.INTEGER,
        attachment_level="D",
    )
    comp_opt = Component(
        "TEST",
        False,
        Role.ATTRIBUTE,
        Concept("TEST"),
        DataType.INTEGER,
        attachment_level="D",
    )

    assert to_pyarrow_type(comp_req) == to_pyarrow_type(comp_opt)


def test_pyarrow_schema():
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
        "REF_AREA",
        True,
        Role.DIMENSION,
        Concept("REF_AREA"),
        DataType.STRING,
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
        False,
        Role.ATTRIBUTE,
        Concept("OBS_STATUS"),
        DataType.STRING,
        local_codes=Codelist(
            "CL_OBS_STATUS",
            agency="BIS",
            items=[Code("A"), Code("E"), Code("M")],
        ),
        attachment_level="D",
    )
    expected = {
        "FREQ": pd.ArrowDtype(pa.string()),
        "REF_AREA": pd.ArrowDtype(pa.string()),
        "TIME_PERIOD": pd.ArrowDtype(pa.string()),
        "OBS_VALUE": pd.ArrowDtype(pa.float64()),
        "OBS_STATUS": pd.ArrowDtype(pa.string()),
    }

    schema = to_pyarrow_schema(Components([c1, c2, c3, c4, c5]))

    assert schema == expected
