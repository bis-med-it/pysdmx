"""Values kept when data go from one data format to another.

The samples have an integer, a long, a boolean, a date time, a decimal,
a string, a float and a double attribute at data set, series and
observation level, some of them without a value, and two data set
attributes without one: `DS_EMPTY`, whose column has no values, and
`DS_ABSENT`, which has no column. `DS_NAN` is a double data set
attribute given as `NaN`, which is a value. `input.csv` gives the date
times with an offset, with `Z` and without a time zone, and decimals
with trailing zeros; the other files give the values as every data
writer must write them, each with its own text for floats and doubles
(`1e-07` and `100.0` in SDMX-CSV, `1e-7` and `100` in SDMX-ML). The
`input_*.xml` files are SDMX-ML messages with the data set
attributes as a provider may give them: a date time with an offset, `1`
for a boolean, an integer with a leading zero and an attribute without a
value. The `groups` files have an attribute attached to a group that only
some series belong to.

The decimal that float64 cannot hold is in columns with an empty value:
the SDMX-CSV readers read a column of numbers without one through
float64 (#776), which is why the data set attribute has none.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pytest

from pysdmx.errors import Invalid
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

# The columns that the SDMX-CSV readers drop: keys and labels
SDMX_CSV_OPTIONS = [
    pytest.param(
        Format.DATA_SDMX_CSV_2_0_0,
        {"keys": "both"},
        "csv_20_keys_both.csv",
        id="csv_20_keys_both",
    ),
    pytest.param(
        Format.DATA_SDMX_CSV_2_0_0,
        {"keys": "series"},
        "csv_20_keys_series.csv",
        id="csv_20_keys_series",
    ),
    pytest.param(
        Format.DATA_SDMX_CSV_2_1_0,
        {"keys": "obs"},
        "csv_21_keys_obs.csv",
        id="csv_21_keys_obs",
    ),
    pytest.param(
        Format.DATA_SDMX_CSV_1_0_0,
        {"labels": "both"},
        "csv_10_labels_both.csv",
        id="csv_10_labels_both",
    ),
    pytest.param(
        Format.DATA_SDMX_CSV_2_0_0,
        {"labels": "both"},
        "csv_20_labels_both.csv",
        id="csv_20_labels_both",
    ),
    pytest.param(
        Format.DATA_SDMX_CSV_2_1_0,
        {"labels": "name"},
        "csv_21_labels_name.csv",
        id="csv_21_labels_name",
    ),
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

SDMX_ML_INPUTS = [
    "input_gen_21.xml",
    "input_str_21.xml",
    "input_str_30.xml",
    "input_str_31.xml",
]

PARTIAL_KEYS = [
    pytest.param(
        Format.DATA_SDMX_CSV_2_0_0,
        {"partial_keys": True},
        "csv_20_partial_keys.csv",
        id="csv_20_partial_keys",
    ),
    pytest.param(
        Format.DATA_SDMX_CSV_2_0_0,
        {"partial_keys": True, "labels": "both"},
        "csv_20_labels_both_partial_keys.csv",
        id="csv_20_labels_both_partial_keys",
    ),
]


def __header():
    return Header(
        id="ID",
        prepared=datetime(2021, 1, 1, tzinfo=timezone.utc),
        sender=Organisation(id="ZZZ"),
    )


def __write(datasets, sdmx_format, params):
    if sdmx_format.name.startswith("DATA_SDMX_ML"):
        params = {**params, "header": __header()}
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
    [*SDMX_CSV, *SDMX_CSV_OPTIONS, *SDMX_ML, *PARTIAL_KEYS],
)
def test_values_are_written_in_their_sdmx_form(sdmx_format, params, filename):
    datasets = get_datasets(DATA, STRUCTURE)

    result = __write(datasets, sdmx_format, params)

    assert result == __expected(filename)


@pytest.mark.parametrize(
    ("sdmx_format", "params", "filename"),
    [*SDMX_CSV, *SDMX_CSV_OPTIONS, *SDMX_ML],
)
def test_values_are_read_back_with_the_same_schema(
    sdmx_format, params, filename
):
    written = __write(get_datasets(DATA, STRUCTURE), sdmx_format, params)

    result = get_datasets(written, STRUCTURE)

    expected = get_datasets(DATA, STRUCTURE)
    assert len(result) == 1
    pd.testing.assert_frame_equal(
        result[0].data, expected[0].data, check_like=True
    )
    assert result[0].attributes == expected[0].attributes


@pytest.mark.parametrize(("sdmx_format", "params", "filename"), SDMX_ML)
def test_writers_leave_the_dataset_as_it_is(sdmx_format, params, filename):
    datasets = get_datasets(DATA, STRUCTURE)
    expected = get_datasets(DATA, STRUCTURE)[0]

    first = __write(datasets, sdmx_format, params)
    second = __write(datasets, sdmx_format, params)
    csv = __write(datasets, Format.DATA_SDMX_CSV_2_0_0, {})

    assert first == second == __expected(filename)
    assert csv == __expected("csv_20.csv")
    pd.testing.assert_frame_equal(datasets[0].data, expected.data)
    assert datasets[0].attributes == expected.attributes


@pytest.mark.parametrize(
    ("sdmx_format", "params", "filename"),
    [*SDMX_CSV, *SDMX_CSV_OPTIONS, *SDMX_ML],
)
def test_data_set_attributes_given_as_python_values(
    sdmx_format, params, filename
):
    # The values that a user gives, instead of those taken from the data
    datasets = get_datasets(DATA, STRUCTURE)
    offset = timezone(timedelta(hours=2))
    datasets[0].attributes = {
        "DS_INT": 7,
        "DS_LONG": 9007199254740993,
        "DS_BOOL": True,
        "DS_DT": datetime(2025, 12, 19, 16, 30, tzinfo=offset),
        "DS_DEC": Decimal("1234.50"),
        "DS_STR": "Data set note",
        "DS_FLT": 1e-07,
        "DS_DBL": 100.0,
        "DS_NAN": float("nan"),
        "DS_EMPTY": None,
        "DS_ABSENT": "",
    }

    result = __write(datasets, sdmx_format, params)

    assert result == __expected(filename)


@pytest.mark.parametrize("filename", SDMX_ML_INPUTS)
def test_data_set_attributes_of_sdmx_ml_get_the_types_of_the_schema(filename):
    result = get_datasets(SAMPLES / filename, STRUCTURE)[0]

    expected = get_datasets(DATA, STRUCTURE)[0]
    assert result.attributes == expected.attributes
    assert list(result.attributes) == list(expected.attributes)
    pd.testing.assert_frame_equal(result.data, expected.data, check_like=True)


@pytest.mark.parametrize("filename", SDMX_ML_INPUTS)
@pytest.mark.parametrize(
    ("sdmx_format", "params", "expected"),
    [
        pytest.param(Format.DATA_SDMX_CSV_2_0_0, {}, "csv_20.csv", id="csv"),
        pytest.param(
            Format.DATA_SDMX_ML_2_1_GEN, SERIES, "gen_21_series.xml", id="gen"
        ),
        pytest.param(
            Format.DATA_SDMX_ML_2_1_STR, SERIES, "str_21_series.xml", id="str"
        ),
        pytest.param(
            Format.DATA_SDMX_ML_3_0, SERIES, "str_30_series.xml", id="str_30"
        ),
        pytest.param(
            Format.DATA_SDMX_ML_3_1, SERIES, "str_31_series.xml", id="str_31"
        ),
    ],
)
def test_data_set_attributes_of_sdmx_ml_are_written_in_their_sdmx_form(
    filename, sdmx_format, params, expected
):
    datasets = get_datasets(SAMPLES / filename, STRUCTURE)

    result = __write(datasets, sdmx_format, params)

    assert result == __expected(expected)


def test_data_set_attribute_of_sdmx_ml_that_does_not_fit_its_type():
    with pytest.raises(Invalid, match="Type conversion failed"):
        get_datasets(SAMPLES / "invalid_data_set_attribute.xml", STRUCTURE)


def test_values_are_read_with_the_types_of_the_schema():
    result = get_datasets(DATA, STRUCTURE)[0]

    expected = get_datasets(SAMPLES / "csv_20.csv", STRUCTURE)[0]
    pd.testing.assert_frame_equal(result.data, expected.data)
    assert result.attributes == expected.attributes
    assert result.attributes["DS_EMPTY"] is None
    assert result.attributes["DS_ABSENT"] is None
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
        "OBS_FLT": pa.float32(),
        "OBS_DBL": pa.float64(),
    }
    # float64 holds every value of the column
    assert result.data["SER_DEC"].dtype == pd.ArrowDtype(pa.float64())


@pytest.mark.parametrize("filename", [x.values[2] for x in SDMX_ML])
def test_values_not_reported_are_read_as_empty_strings(filename):
    result = __data(filename)

    expected = __data("csv_20.csv")[result.columns]
    assert (expected == "").any(axis=None)
    pd.testing.assert_frame_equal(result == "", expected == "")
    # Each format has its own text for floats and doubles
    same_text = [
        name for name in result.columns if not name.endswith(("_FLT", "_DBL"))
    ]
    pd.testing.assert_frame_equal(result[same_text], expected[same_text])


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
