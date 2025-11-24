from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io import read_sdmx
from pysdmx.toolkit.pd._data_utils import (
    format_labels,
    fill_na_values,
    NUMERIC_TYPES,
)
from pysdmx.model.concept import DataType
from pysdmx.errors import Invalid


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

    format_labels(data, labels="name", components=dsd.components)
    assert "DIMENSION 1" in data.columns
    assert "DIMENSION 2" in data.columns
    assert "ATTRIBUTE 1" in data.columns
    assert "ATTRIBUTE 2" in data.columns
    assert "OBS VALUE" in data.columns
    assert "TIME PERIOD" in data.columns


def test_write_labels_both(data_path_optional, dsd_path):
    result = read_sdmx(dsd_path).get_data_structure_definitions()
    dsd = result[0]
    data = pd.read_json(data_path_optional, orient="records")

    format_labels(data, labels="both", components=dsd.components)
    assert "DIM1:DIMENSION 1" in data.columns
    assert "DIM2:DIMENSION 2" in data.columns
    assert "ATT1:ATTRIBUTE 1" in data.columns
    assert "ATT2:ATTRIBUTE 2" in data.columns
    assert "OBS_VALUE:OBS VALUE" in data.columns
    assert "TIME_PERIOD:TIME PERIOD" in data.columns


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


def test_fill_na_values_raises_when_no_components():
    data = pd.DataFrame({"a": [None]})
    structure = object()

    with pytest.raises(Invalid):
        fill_na_values(data, structure)


@pytest.mark.parametrize("dtype", list(NUMERIC_TYPES))
def test_fill_na_values_numeric_and_non_numeric(dtype):
    data = pd.DataFrame({"num": [None, 1], "cat": [None, "x"]})

    class SimpleComp:
        def __init__(self, id_, dtype_):
            self.id = id_
            self.dtype = dtype_

    structure = type("S", (), {})()
    structure.components = [
        SimpleComp("num", dtype),
        SimpleComp("cat", DataType.STRING),
    ]

    out = fill_na_values(data.copy(), structure)

    assert out["num"].iloc[0] == "NaN"
    assert out["cat"].iloc[0] == "#N/A"
