from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io import read_sdmx
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
