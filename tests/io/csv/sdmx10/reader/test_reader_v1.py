from pathlib import Path

import pytest

from pysdmx.io.csv.sdmx10.reader import read


@pytest.fixture()
def data_path():
    base_path = Path(__file__).parent / "samples" / "data_v1.csv"
    return str(base_path)


def test_reading_data_v1(data_path):
    with open(data_path, "r") as f:
        infile = f.read()
    dataset_dict = read(infile)
    assert 'BIS:BIS_DER(1.0)' in dataset_dict
    df = dataset_dict['BIS:BIS_DER(1.0)'].data
    assert len(df) == 1000
    assert "DATAFLOW" not in df.columns

