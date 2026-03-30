import pandas as pd
import pyarrow as pa
import pytest

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
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
