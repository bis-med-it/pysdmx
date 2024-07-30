from pathlib import Path

import pytest

from pysdmx.errors import ClientError
from pysdmx.io.csv.sdmx10.reader import read


@pytest.fixture()
def data_path():
    base_path = Path(__file__).parent / "samples" / "data_v1.csv"
    return str(base_path)


@pytest.fixture()
def data_path_exception():
    base_path = Path(__file__).parent / "samples" / "data_v1_exception.csv"
    return str(base_path)


@pytest.fixture()
def data_path_no_freq():
    base_path = Path(__file__).parent / "samples" / "data_v1_no_freq_cols.csv"
    return base_path


def test_reading_data_v1(data_path):
    with open(data_path, "r") as f:
        infile = f.read()
    dataset_dict = read(infile)
    assert "dataflow=BIS:BIS_DER(1.0)" in dataset_dict
    df = dataset_dict["dataflow=BIS:BIS_DER(1.0)"].data
    assert len(df) == 1000
    assert "DATAFLOW" not in df.columns


def test_reading_data_v1_exception(data_path_exception):
    with open(data_path_exception, "r") as f:
        infile = f.read()
    with pytest.raises(ClientError, match="Invalid SDMX-CSV 1.0"):
        read(infile)


def test_reading_no_freq_v1(data_path_no_freq):
    with open(data_path_no_freq, "r") as f:
        infile = f.read()
    dataset_dict = read(infile)
    assert "dataflow=WB:GCI(1.0):GlobalCompetitivenessIndex" in dataset_dict
    df = dataset_dict["dataflow=WB:GCI(1.0):GlobalCompetitivenessIndex"].data
    assert len(df) == 7
    assert "DATAFLOW" not in df.columns
