"""Values kept when data go from one data format to another.

The samples have an integer, a long, a boolean, a date time, a decimal
and a string attribute at data set, series and observation level, some
of them without a value. `input.csv` gives the date times with an
offset, with `Z` and without a time zone, and decimals with trailing
zeros; the other files give the values as every data writer must write
them. The `groups` files have an attribute attached to a group that only
some series belong to.

The decimal that float64 cannot hold is in columns with an empty value:
the SDMX-CSV readers read a column of numbers without one through
float64 (#776), which is why the data set attribute has none.
"""

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pytest

from pysdmx.io import get_datasets, read_sdmx, write_sdmx
from pysdmx.io.format import Format
from pysdmx.model import Organisation
from pysdmx.model.message import Header

SAMPLES = Path(__file__).parent / "samples" / "round_trip"
STRUCTURE = SAMPLES / "datastructure.xml"
DATA = SAMPLES / "input.csv"

FLAT = {"dimension_at_observation": "AllDimensions"}
SERIES = {"dimension_at_observation": "TIME_PERIOD"}

SDMX_CSV = [
    pytest.param(Format.DATA_SDMX_CSV_1_0_0, {}, "csv_10.csv", id="csv_10"),
    pytest.param(Format.DATA_SDMX_CSV_2_0_0, {}, "csv_20.csv", id="csv_20"),
    pytest.param(Format.DATA_SDMX_CSV_2_1_0, {}, "csv_21.csv", id="csv_21"),
]

SDMX_ML = [
    pytest.param(
        Format.DATA_SDMX_ML_2_1_GEN, FLAT, "gen_21_all.xml", id="gen_21_all"
    ),
    pytest.param(
        Format.DATA_SDMX_ML_2_1_GEN,
        SERIES,
        "gen_21_series.xml",
        id="gen_21_series",
    ),
    pytest.param(
        Format.DATA_SDMX_ML_2_1_GENTS, SERIES, "gen_21_ts.xml", id="gen_21_ts"
    ),
    pytest.param(
        Format.DATA_SDMX_ML_2_1_STR, FLAT, "str_21_all.xml", id="str_21_all"
    ),
    pytest.param(
        Format.DATA_SDMX_ML_2_1_STR,
        SERIES,
        "str_21_series.xml",
        id="str_21_series",
    ),
    pytest.param(
        Format.DATA_SDMX_ML_2_1_STRTS, SERIES, "str_21_ts.xml", id="str_21_ts"
    ),
    pytest.param(
        Format.DATA_SDMX_ML_3_0, FLAT, "str_30_all.xml", id="str_30_all"
    ),
    pytest.param(
        Format.DATA_SDMX_ML_3_0,
        SERIES,
        "str_30_series.xml",
        id="str_30_series",
    ),
    pytest.param(
        Format.DATA_SDMX_ML_3_1, FLAT, "str_31_all.xml", id="str_31_all"
    ),
    pytest.param(
        Format.DATA_SDMX_ML_3_1,
        SERIES,
        "str_31_series.xml",
        id="str_31_series",
    ),
]

PARTIAL_KEYS = pytest.param(
    Format.DATA_SDMX_CSV_2_0_0,
    {"partial_keys": True},
    "csv_20_partial_keys.csv",
    id="csv_20_partial_keys",
)


def __write(sdmx_format, params):
    datasets = get_datasets(DATA, STRUCTURE)
    if sdmx_format.name.startswith("DATA_SDMX_ML"):
        header = Header(
            id="ID",
            prepared=datetime(2021, 1, 1, tzinfo=timezone.utc),
            sender=Organisation(id="ZZZ"),
        )
        params = {**params, "header": header}
    return write_sdmx(datasets, sdmx_format, **params)


def __expected(filename):
    if filename.endswith(".xml"):
        with open(SAMPLES / filename, "r") as f:
            return f.read()
    with open(SAMPLES / filename, "rb") as f:
        return f.read().decode("utf-8")


def __data(filename):
    # The data as they are read without a schema
    return read_sdmx(SAMPLES / filename).data[0].data


@pytest.mark.parametrize(
    ("sdmx_format", "params", "filename"),
    [*SDMX_CSV, *SDMX_ML, PARTIAL_KEYS],
)
def test_values_are_written_in_their_sdmx_form(sdmx_format, params, filename):
    result = __write(sdmx_format, params)

    assert result == __expected(filename)


@pytest.mark.parametrize(
    ("sdmx_format", "params", "filename"), [*SDMX_CSV, *SDMX_ML]
)
def test_values_are_read_back_with_the_same_schema(
    sdmx_format, params, filename
):
    written = __write(sdmx_format, params)

    result = get_datasets(written, STRUCTURE)

    expected = get_datasets(DATA, STRUCTURE)
    assert len(result) == 1
    pd.testing.assert_frame_equal(
        result[0].data, expected[0].data, check_like=True
    )
    assert result[0].attributes == expected[0].attributes


def test_values_are_read_with_the_types_of_the_schema():
    result = get_datasets(DATA, STRUCTURE)[0]

    expected = get_datasets(SAMPLES / "csv_20.csv", STRUCTURE)[0]
    pd.testing.assert_frame_equal(result.data, expected.data)
    assert result.attributes == expected.attributes
    dtypes = {
        name: dtype.pyarrow_dtype
        for name, dtype in result.data.dtypes.items()
        if name.startswith("OBS_")
    }
    assert dtypes == {
        "OBS_VALUE": pa.int32(),
        "OBS_INT": pa.int32(),
        "OBS_LONG": pa.int64(),
        "OBS_BOOL": pa.bool_(),
        "OBS_DT": pa.timestamp("ns", tz="UTC"),
        # float64 cannot hold every value of the column
        "OBS_DEC": pa.decimal128(38, 9),
        "OBS_STR": pa.string(),
    }
    # float64 holds every value of the column
    assert result.data["SER_DEC"].dtype == pd.ArrowDtype(pa.float64())


@pytest.mark.parametrize("filename", [x.values[2] for x in SDMX_ML])
def test_values_not_reported_are_read_as_empty_strings(filename):
    result = __data(filename)

    expected = __data("csv_20.csv")[result.columns]
    assert (expected == "").any(axis=None)
    pd.testing.assert_frame_equal(result, expected)


@pytest.mark.parametrize(
    "filename",
    [
        "groups_gen_21.xml",
        "groups_str_21.xml",
        "groups_str_30.xml",
        "groups_str_31.xml",
    ],
)
def test_group_attributes_not_reported_are_read_as_empty_strings(filename):
    result = __data(filename)

    expected = __data("groups.csv")
    assert (expected["GRP_STR"] == "").any()
    pd.testing.assert_frame_equal(result, expected, check_like=True)
