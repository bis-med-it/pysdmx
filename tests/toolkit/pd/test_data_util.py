from pathlib import Path

import pandas as pd
import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.toolkit.pd import drop_labels
from pysdmx.toolkit.pd._data_utils import format_labels


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
            "DIM1: DIMENSION 1": ["A: Value A"],
            "OBS_VALUE": ["12.4"],
            "EMBARGO_TIME": ["2025-12-19T14:30:00Z"],
        }
    )
    df = drop_labels(df)
    assert "DIM1" in df.columns
    assert df.at[0, "DIM1"] == "A"
    assert df.at[0, "OBS_VALUE"] == "12.4"
    assert df.at[0, "EMBARGO_TIME"] == "2025-12-19T14:30:00Z"


def test_drop_labels_name_format():
    df = pd.DataFrame(
        {
            "STRUCTURE": ["dataflow"],
            "STRUCTURE_ID": ["MD:MD_TEST(1.0)"],
            "STRUCTURE_NAME": ["MD TEST"],
            "ACTION": ["I"],
            "DIM1": ["A"],
            "DIMENSION 1": ["Value A"],
            "OBS_VALUE": ["12.4"],
            "Observation value": [""],
        }
    )
    df = drop_labels(df)
    assert list(df.columns) == [
        "STRUCTURE",
        "STRUCTURE_ID",
        "ACTION",
        "DIM1",
        "OBS_VALUE",
    ]
    assert df.at[0, "DIM1"] == "A"


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
