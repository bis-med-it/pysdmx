from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

import pandas as pd
import pyarrow as pa
import pytest

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset, format_value
from pysdmx.model import (
    Component,
    Components,
    Concept,
    DataType,
    Role,
    Schema,
)


def _make_schema(*comps):
    return Schema(
        context="dataflow",
        agency="BIS",
        id="TEST",
        components=Components(list(comps)),
    )


def _dim(id_, dt=DataType.STRING):
    return Component(id_, True, Role.DIMENSION, Concept(id_), dt)


def _msr(id_, dt=DataType.DOUBLE):
    return Component(id_, True, Role.MEASURE, Concept(id_), dt)


def _att(id_, dt=DataType.STRING):
    return Component(
        id_, False, Role.ATTRIBUTE, Concept(id_), dt, attachment_level="D"
    )


# --- Schema-based tests ---


def test_schema_typed_columns():
    schema = _make_schema(
        _dim("FREQ"),
        _dim("TIME_PERIOD", DataType.PERIOD),
        _msr("OBS_VALUE", DataType.DOUBLE),
    )
    df = pd.DataFrame(
        {
            "FREQ": ["A", "M"],
            "TIME_PERIOD": ["2020", "2021"],
            "OBS_VALUE": [1.5, 2.5],
        }
    )

    ds = PandasDataset(structure=schema, data=df)

    assert ds.data["FREQ"].dtype == pd.ArrowDtype(pa.string())
    assert ds.data["TIME_PERIOD"].dtype == pd.ArrowDtype(pa.string())
    assert ds.data["OBS_VALUE"].dtype == pd.ArrowDtype(pa.float64())


def test_schema_columns_not_in_schema_become_string():
    schema = _make_schema(_dim("FREQ"))
    df = pd.DataFrame({"FREQ": ["A"], "EXTRA": ["X"]})

    ds = PandasDataset(structure=schema, data=df)

    assert ds.data["EXTRA"].dtype == pd.ArrowDtype(pa.string())


def test_schema_columns_not_in_df_are_skipped():
    schema = _make_schema(_dim("FREQ"), _dim("MISSING"))
    df = pd.DataFrame({"FREQ": ["A"]})

    ds = PandasDataset(structure=schema, data=df)

    assert ds.data["FREQ"].dtype == pd.ArrowDtype(pa.string())
    assert "MISSING" not in ds.data.columns


def test_schema_empty_dataframe():
    schema = _make_schema(_dim("FREQ"))
    df = pd.DataFrame({"FREQ": pd.Series([], dtype="object")})

    ds = PandasDataset(structure=schema, data=df)

    assert ds.data["FREQ"].dtype == pd.ArrowDtype(pa.string())


def test_schema_nullable_values_preserved():
    schema = _make_schema(
        _dim("ID"),
        _msr("VALUE", DataType.INTEGER),
    )
    df = pd.DataFrame({"ID": ["A", "B"], "VALUE": [1, None]})

    ds = PandasDataset(structure=schema, data=df)

    assert ds.data["VALUE"].dtype == pd.ArrowDtype(pa.int32())
    assert pd.isna(ds.data["VALUE"].iloc[1])


def test_schema_conversion_failure_raises_invalid():
    schema = _make_schema(
        _dim("ID"),
        _msr("VALUE", DataType.INTEGER),
    )
    df = pd.DataFrame({"ID": ["A"], "VALUE": ["not_a_number"]})

    with pytest.raises(Invalid):
        PandasDataset(structure=schema, data=df)


@pytest.mark.parametrize(
    "value",
    ["not_a_date_time", "now", "today", "nan", "NaT", "2025-13-45T00:00:00"],
)
def test_schema_date_time_conversion_failure_raises_invalid(value):
    schema = _make_schema(
        _dim("ID"),
        _att("UPDATED", DataType.DATE_TIME),
    )
    df = pd.DataFrame(
        {"ID": ["A", "B"], "UPDATED": ["2025-12-19T14:30:00Z", value]}
    )

    with pytest.raises(Invalid, match="Type conversion failed"):
        PandasDataset(structure=schema, data=df)


# --- Decimal tests ---

FLOAT64 = pd.ArrowDtype(pa.float64())


def _decimals(values):
    schema = _make_schema(_dim("ID"), _att("VALUE", DataType.DECIMAL))
    ids = [str(i) for i in range(len(values))]
    df = pd.DataFrame({"ID": ids, "VALUE": values})
    return PandasDataset(structure=schema, data=df)


@pytest.mark.parametrize(
    "values",
    [
        ["0.10", "1.5", "1234.5", None, ""],
        # More than 15 digits, that float64 holds all the same
        ["0.1000000000000000", "123456789012345.5"],
        # NaN and numbers with an exponent are kept as float64 has them
        ["0.1000000000000000", "NaN", "1e-7"],
        ["1.2345678901234567e-5", "NaN"],
        [0.1, 1.5, None],
        [1, 2],
        [Decimal("0.10"), Decimal("1.5"), None],
    ],
)
def test_schema_decimals_that_float64_holds_are_float64(values):
    ds = _decimals(values)

    assert ds.data["VALUE"].dtype == FLOAT64


@pytest.mark.parametrize(
    ("values", "scale"),
    [
        (["1234567890.123456789", "0.10", None, ""], 9),
        # The trailing zeros do not count for the scale
        (["12345678901234567.25", "1.5000"], 2),
        (["12345678901234567890", "100"], 0),
        # A number with an exponent is kept if it fits the scale
        (["1234567890.123456789", "1e3"], 9),
        ([Decimal("1234567890.123456789"), Decimal("0.10"), None], 9),
        # Integers beyond 2**53
        ([9007199254740993, 1], 0),
    ],
)
def test_schema_decimals_that_float64_alters_are_decimal(values, scale):
    ds = _decimals(values)

    assert ds.data["VALUE"].dtype == pd.ArrowDtype(pa.decimal128(38, scale))
    result = ds.data["VALUE"].astype(object).tolist()
    for value, decimal in zip(values, result):
        if value in (None, ""):
            assert pd.isna(decimal)
        else:
            assert decimal == Decimal(str(value))


def test_schema_decimal_column_keeps_its_decimals():
    values = [Decimal("1234567890.123456789"), Decimal("0.10"), None]
    column = pd.Series(values, dtype=pd.ArrowDtype(pa.decimal128(38, 18)))

    ds = _decimals(column)

    assert ds.data["VALUE"].dtype == pd.ArrowDtype(pa.decimal128(38, 9))
    assert ds.data["VALUE"].iloc[0] == values[0]
    assert ds.data["VALUE"].iloc[1] == values[1]
    assert pd.isna(ds.data["VALUE"].iloc[2])


def test_reassign_structure_keeps_decimals():
    ds = _decimals(["1234567890.123456789", "0.10", None])

    ds.structure = ds.structure

    assert ds.data["VALUE"].dtype == pd.ArrowDtype(pa.decimal128(38, 9))
    assert ds.data["VALUE"].iloc[0] == Decimal("1234567890.123456789")


@pytest.mark.parametrize(
    "values",
    [
        ["not_a_number"],
        ["1234567890.123456789", "not_a_number"],
        # A decimal column has no NaN
        ["1234567890.123456789", "NaN"],
        # More digits than a decimal holds
        ["1" * 39],
        ["1234567890.123456789", "1e-12"],
    ],
)
def test_schema_decimal_conversion_failure_raises_invalid(values):
    with pytest.raises(Invalid, match="Type conversion failed"):
        _decimals(values)


# --- URN-based tests ---


def test_urn_all_columns_string():
    df = pd.DataFrame({"A": [1, 2], "B": ["x", "y"]})

    ds = PandasDataset(structure="Dataflow=BIS:TEST(1.0)", data=df)

    assert ds.data["A"].dtype == pd.ArrowDtype(pa.string())
    assert ds.data["B"].dtype == pd.ArrowDtype(pa.string())


def test_urn_empty_dataframe():
    df = pd.DataFrame()

    ds = PandasDataset(structure="Dataflow=BIS:TEST(1.0)", data=df)

    assert ds.data.empty


# --- Structure reassignment tests ---


def test_reassign_structure_updates_dtypes():
    df = pd.DataFrame({"FREQ": ["A"], "VALUE": ["1.5"]})
    ds = PandasDataset(structure="Dataflow=BIS:TEST(1.0)", data=df)
    assert ds.data["VALUE"].dtype == pd.ArrowDtype(pa.string())

    schema = _make_schema(
        _dim("FREQ"),
        _msr("VALUE", DataType.DOUBLE),
    )
    ds.structure = schema

    assert ds.data["VALUE"].dtype == pd.ArrowDtype(pa.float64())


def test_reassign_structure_keeps_date_times_in_utc():
    schema = _make_schema(
        _dim("ID"),
        _att("UPDATED", DataType.DATE_TIME),
    )
    df = pd.DataFrame(
        {"ID": ["A", "B"], "UPDATED": ["2025-12-19T14:30:00+02:00", None]}
    )
    ds = PandasDataset(structure=schema, data=df)

    ds.structure = schema

    utc = pd.ArrowDtype(pa.timestamp("ns", tz="UTC"))
    assert ds.data["UPDATED"].dtype == utc
    assert ds.data["UPDATED"].iloc[0] == pd.Timestamp("2025-12-19T12:30:00Z")
    assert pd.isna(ds.data["UPDATED"].iloc[1])


# --- Regression tests ---


def test_stringify_dataframe():
    from pysdmx.io.pd import stringify_dataframe

    df = pd.DataFrame({"A": [1, None], "B": ["x", None]})
    ds = PandasDataset(structure="Dataflow=BIS:TEST(1.0)", data=df)
    result = stringify_dataframe(ds.data)
    assert result["A"].tolist() == ["1", ""]
    assert result["B"].tolist() == ["x", ""]
    # All columns should use the plain string dtype of the installed pandas
    # version (object in pandas 2, str in pandas 3)
    plain_str = pd.Series(dtype=str).dtype
    assert all(result[c].dtype == plain_str for c in result.columns)


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        (True, "true"),
        (False, "false"),
        (1, "1"),
        (9007199254740993, "9007199254740993"),
        ("text", "text"),
        (date(2020, 1, 5), "2020-01-05"),
        (datetime(2025, 12, 19, 14, 30), "2025-12-19T14:30:00Z"),
        (
            datetime(2025, 12, 19, 14, 30, 0, 500000),
            "2025-12-19T14:30:00.5Z",
        ),
        (
            datetime(
                2025, 12, 19, 14, 30, tzinfo=timezone(timedelta(hours=2))
            ),
            "2025-12-19T12:30:00Z",
        ),
        (pd.Timestamp("2025-12-19T14:30:10"), "2025-12-19T14:30:10Z"),
        (Decimal("1234567890.123456789"), "1234567890.123456789"),
        (Decimal("0.100000000"), "0.1"),
        (Decimal("-0.000000001"), "-0.000000001"),
        (Decimal("100.000"), "100"),
        (Decimal("1E+2"), "100"),
        (Decimal("0E-9"), "0"),
        (
            pd.Timestamp("2025-12-19T14:30:00.123456789+02:00"),
            "2025-12-19T12:30:00.123456789Z",
        ),
    ],
)
def test_format_value(value, expected):
    assert format_value(value) == expected


def test_stringify_dataframe_empty():
    from pysdmx.io.pd import stringify_dataframe

    df = pd.DataFrame()
    result = stringify_dataframe(df)
    assert result.empty


def test_regression_509_all_none_column():
    """Regression test for #509.

    Dictionary-encoded columns with all-None values previously caused
    ArrowNotImplementedError in the XML structure-specific writer.
    PandasDataset now ensures all columns use well-known pyarrow types.
    """
    df = pd.DataFrame(
        {
            "DIM": ["A", "B"],
            "OBS_VALUE": ["1.0", "2.0"],
            "ATTR": [None, None],
        }
    )

    ds = PandasDataset(structure="Dataflow=BIS:TEST(1.0)", data=df)

    # All columns should be string[pyarrow], not dictionary
    assert ds.data["ATTR"].dtype == pd.ArrowDtype(pa.string())
    # Verify no ArrowNotImplementedError on the writers' string conversion
    from pysdmx.io.pd import stringify_dataframe

    result = stringify_dataframe(ds.data)
    assert result["ATTR"].tolist() == ["", ""]
