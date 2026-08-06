from io import StringIO
from pathlib import Path

import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.toolkit.pd import drop_labels
from pysdmx.toolkit.pd._data_utils import format_labels

# labels=name example from the SDMX-CSV 2.0.0 field guide: each id
# column directly precedes its localised name column; the name cell is
# empty when the value has no localised name (OBS_VALUE) and repeats
# the value for time periods (DIM_3).
SDMX_CSV_20_LABELS_NAME = (
    "STRUCTURE,STRUCTURE_ID,STRUCTURE_NAME,ACTION,"
    "DIM_1,Dimension 1,DIM_2,Dimension 2,DIM_3,Dimension 3,"
    "OBS_VALUE,Observation value,ATTR_1,Attribute 1\n"
    "dataflow,ESTAT:NA_MAIN(1.6.0),National Accounts Main Aggregates,I,"
    "A,Value A,B,Value B,2014-01,2014-01,12.4,,Y,Yes\n"
)

# labels=both example from the SDMX-CSV 1.0 field guide
SDMX_CSV_10_LABELS_BOTH = (
    "DATAFLOW,DIM_1: Dimension 1,DIM_2: Dimension 2,OBS_VALUE\n"
    "ESTAT:NA_MAIN(1.6): National Accounts Main Aggregates,"
    "A: Value A,B: Value B,12.4\n"
)


@pytest.fixture
def data_path_optional():
    base_path = Path(__file__).parent / "samples" / "df_optional.json"
    return str(base_path)


@pytest.fixture
def data_path_optional_names():
    base_path = Path(__file__).parent / "samples" / "df_optional_names.json"
    return str(base_path)


@pytest.fixture
def dsd_path():
    base_path = Path(__file__).parent / "samples" / "datastructure.xml"
    return str(base_path)


def test_write_labels_name(data_path_optional, dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    data = pd.read_json(data_path_optional, orient="records")
    data["EXTRA"] = "x"

    format_labels(data, labels="name", components=dsd.components)
    assert list(data.columns) == [
        "DIM1",
        "DIMENSION 1",
        "DIM2",
        "DIMENSION 2",
        "ATT1",
        "ATTRIBUTE 1",
        "ATT2",
        "ATTRIBUTE 2",
        "OBS_VALUE",
        "OBS VALUE",
        "TIME_PERIOD",
        "TIME PERIOD",
        "EXTRA",
    ]
    assert (data["DIMENSION 1"] == data["DIM1"]).all()


def test_write_labels_name_duplicated(data_path_optional, dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    data = pd.read_json(data_path_optional, orient="records")
    data["DIMENSION 1"] = "x"

    with pytest.raises(Invalid, match="DIMENSION 1"):
        format_labels(data, labels="name", components=dsd.components)


def test_write_labels_both(data_path_optional, dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    data = pd.read_json(data_path_optional, orient="records")

    format_labels(data, labels="both", components=dsd.components)
    assert "DIM1: DIMENSION 1" in data.columns
    assert "DIM2: DIMENSION 2" in data.columns
    assert "ATT1: ATTRIBUTE 1" in data.columns
    assert "ATT2: ATTRIBUTE 2" in data.columns
    assert "OBS_VALUE: OBS VALUE" in data.columns
    assert "TIME_PERIOD: TIME PERIOD" in data.columns


def test_write_labels_id(data_path_optional_names, dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    data = pd.read_json(data_path_optional_names, orient="records")

    format_labels(data, labels="id", components=dsd.components)
    assert "DIM1" in data.columns
    assert "DIM2" in data.columns
    assert "ATT1" in data.columns
    assert "ATT2" in data.columns
    assert "OBS_VALUE" in data.columns
    assert "TIME_PERIOD" in data.columns


def test_format_drop_labels_name_roundtrip(data_path_optional, dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    original = pd.read_json(data_path_optional, orient="records").astype(str)

    data = original.copy()
    format_labels(data, labels="name", components=dsd.components)
    # The writer adds STRUCTURE_NAME, which drop_labels uses to detect
    # the labels=name format
    data.insert(0, "STRUCTURE_NAME", "MD TEST")
    data = drop_labels(data)

    pd.testing.assert_frame_equal(data, original)


def test_format_drop_labels_both_roundtrip(data_path_optional, dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    original = pd.read_json(data_path_optional, orient="records").astype(str)

    data = original.copy()
    format_labels(data, labels="both", components=dsd.components)
    data = drop_labels(data)

    pd.testing.assert_frame_equal(data, original)


def test_drop_labels_both_format():
    df = pd.DataFrame(
        {
            "DIM_1: Dimension 1": ["A: Value A"],
            "OBS_VALUE": ["12.4"],
            "EMBARGO_TIME: Embargo time": ["2025-12-19T14:30:00Z"],
        }
    )
    df = drop_labels(df)
    assert df.at[0, "DIM_1"] == "A"
    assert df.at[0, "OBS_VALUE"] == "12.4"
    # A bare ':' inside a value (e.g. a full datetime) is preserved
    assert df.at[0, "EMBARGO_TIME"] == "2025-12-19T14:30:00Z"


def test_drop_labels_both_format_v1_field_guide():
    df = pd.read_csv(StringIO(SDMX_CSV_10_LABELS_BOTH))
    df = drop_labels(df)
    assert df.at[0, "DIM_1"] == "A"
    assert df.at[0, "DIM_2"] == "B"
    assert df.at[0, "OBS_VALUE"] == 12.4
    # The label on the structure id cell is stripped by the CSV
    # readers, not by drop_labels
    assert (
        df.at[0, "DATAFLOW"]
        == "ESTAT:NA_MAIN(1.6): National Accounts Main Aggregates"
    )


def test_drop_labels_name_format():
    df = pd.read_csv(StringIO(SDMX_CSV_20_LABELS_NAME), keep_default_na=False)
    df = drop_labels(df)
    assert list(df.columns) == [
        "STRUCTURE",
        "STRUCTURE_ID",
        "ACTION",
        "DIM_1",
        "DIM_2",
        "DIM_3",
        "OBS_VALUE",
        "ATTR_1",
    ]
    assert df.iloc[0].tolist() == [
        "dataflow",
        "ESTAT:NA_MAIN(1.6.0)",
        "I",
        "A",
        "B",
        "2014-01",
        12.4,
        "Y",
    ]


def test_drop_labels_name_format_with_keys():
    df = pd.DataFrame(
        {
            "STRUCTURE": ["dataflow"],
            "STRUCTURE_ID": ["ESTAT:NA_MAIN(1.6.0)"],
            "STRUCTURE_NAME": ["National Accounts Main Aggregates"],
            "ACTION": ["I"],
            "SERIES_KEY": ["A.B"],
            "OBS_KEY": ["A.B.2014-01"],
            "DIM_1": ["A"],
            "Dimension 1": ["Value A"],
            "OBS_VALUE": ["12.4"],
            "Observation value": [""],
        }
    )
    df = drop_labels(df)
    # The keys columns have no name column and do not break the
    # id/name pairing
    assert list(df.columns) == [
        "STRUCTURE",
        "STRUCTURE_ID",
        "ACTION",
        "SERIES_KEY",
        "OBS_KEY",
        "DIM_1",
        "OBS_VALUE",
    ]
    assert df.at[0, "DIM_1"] == "A"


def test_drop_labels_name_format_malformed():
    df = pd.DataFrame(
        {
            "STRUCTURE_NAME": ["MD TEST"],
            "DIM1": ["A"],
            "DIMENSION 1": ["Value A"],
            "OBS_VALUE": ["12.4"],
        }
    )
    with pytest.raises(Invalid, match="odd number of component columns"):
        drop_labels(df)


def test_drop_labels_no_labels():
    df = pd.DataFrame({"DIM1": ["A"], "OBS_VALUE": ["12.4"]})
    result = drop_labels(df)
    assert list(result.columns) == ["DIM1", "OBS_VALUE"]
