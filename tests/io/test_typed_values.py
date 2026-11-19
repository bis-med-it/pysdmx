"""Integers, booleans and date times in the data readers and writers.

The samples have a typed attribute of each kind at data set, series and
observation level. `input.csv` gives the date times with an offset, with
`Z` and without a time zone; the other files give the values as every
data writer must write them.
"""

from datetime import datetime, timezone
from pathlib import Path

import pandas as pd
import pyarrow as pa
import pytest

from pysdmx.io import get_datasets, write_sdmx
from pysdmx.io.format import Format
from pysdmx.model import Organisation
from pysdmx.model.message import Header

SAMPLES = Path(__file__).parent / "samples" / "typed_values"
STRUCTURE = SAMPLES / "datastructure.xml"
DATA = SAMPLES / "input.csv"

FLAT = {"dimension_at_observation": "AllDimensions"}
SERIES = {"dimension_at_observation": "TIME_PERIOD"}

WRITERS = [
    pytest.param(Format.DATA_SDMX_CSV_1_0_0, {}, "csv_10.csv", id="csv_10"),
    pytest.param(Format.DATA_SDMX_CSV_2_0_0, {}, "csv_20.csv", id="csv_20"),
    pytest.param(Format.DATA_SDMX_CSV_2_1_0, {}, "csv_21.csv", id="csv_21"),
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
        Format.DATA_SDMX_ML_2_1_STR, FLAT, "str_21_all.xml", id="str_21_all"
    ),
    pytest.param(
        Format.DATA_SDMX_ML_2_1_STR,
        SERIES,
        "str_21_series.xml",
        id="str_21_series",
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


@pytest.mark.parametrize(
    ("sdmx_format", "params", "filename"), [*WRITERS, PARTIAL_KEYS]
)
def test_typed_values_are_written_in_their_sdmx_form(
    sdmx_format, params, filename
):
    result = __write(sdmx_format, params)

    assert result == __expected(filename)


@pytest.mark.parametrize(("sdmx_format", "params", "filename"), WRITERS)
def test_typed_values_are_read_back_with_the_same_schema(
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


def test_date_times_are_read_as_utc():
    result = get_datasets(DATA, STRUCTURE)[0]

    expected = get_datasets(SAMPLES / "csv_20.csv", STRUCTURE)[0]
    utc = pd.ArrowDtype(pa.timestamp("ns", tz="UTC"))
    assert result.data["SER_DT"].dtype == utc
    assert result.data["OBS_DT"].dtype == utc
    pd.testing.assert_frame_equal(result.data, expected.data)
    assert result.attributes == expected.attributes
