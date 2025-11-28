from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.csv.sdmx10.reader import read


@pytest.fixture
def data_path():
    base_path = Path(__file__).parent / "samples" / "data_v1.csv"
    return str(base_path)


@pytest.fixture
def data_path_exception():
    base_path = Path(__file__).parent / "samples" / "data_v1_exception.csv"
    return str(base_path)


@pytest.fixture
def data_path_no_freq():
    base_path = Path(__file__).parent / "samples" / "data_v1_no_freq_cols.csv"
    return base_path


@pytest.fixture
def csv_labels_both():
    base_path = Path(__file__).parent / "samples" / "csv_labels_both.csv"
    return base_path


@pytest.fixture
def data_v1_nulls():
    return Path(__file__).parent / "samples" / "data_v1_nulls.csv"


def test_reading_data_v1(data_path):
    with open(data_path, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert datasets[0].short_urn == "Dataflow=BIS:BIS_DER(1.0)"
    df = datasets[0].data
    assert len(df) == 1000
    assert "DATAFLOW" not in df.columns


def test_reading_sdmx_csv_v1(data_path):
    datasets = read_sdmx(data_path).data
    assert datasets[0].short_urn == "Dataflow=BIS:BIS_DER(1.0)"
    df = datasets[0].data
    assert len(df) == 1000
    assert "DATAFLOW" not in df.columns
    assert len(datasets[0].attributes) == 0


def test_reading_sdmx_csv_v1_string(data_path):
    with open(data_path, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert datasets[0].short_urn == "Dataflow=BIS:BIS_DER(1.0)"
    df = datasets[0].data
    assert len(df) == 1000
    assert "DATAFLOW" not in df.columns
    assert len(datasets[0].attributes) == 0


def test_reading_data_v1_exception(data_path_exception):
    with open(data_path_exception, "r") as f:
        infile = f.read()
    with pytest.raises(Invalid, match="Invalid SDMX-CSV 1.0"):
        read(infile)


def test_reading_no_freq_v1(data_path_no_freq):
    with open(data_path_no_freq, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert datasets[0].short_urn == "Dataflow=WB:GCI(1.0)"
    df = datasets[0].data
    assert len(df) == 7
    assert "DATAFLOW" not in df.columns


def test_reading_labels_both(csv_labels_both):
    with open(csv_labels_both, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert datasets[0].short_urn == "Dataflow=MD:MD_TEST(1.0)"
    df = datasets[0].data
    assert "ATT1" in df.columns
    assert df.at[0, "ATT1"] == "C"
    assert len(df) == 1
    assert "DATAFLOW" not in df.columns


def test_read_csv_v1_nulls(data_v1_nulls):
    msg = read_sdmx(data_v1_nulls)
    df = msg.data[0].data

    # Check NaN value
    row_nan = df[df["TIME_PERIOD"] == "2002"].iloc[0]
    assert row_nan["OBS_VALUE"] == "NaN"
    assert isinstance(row_nan["OBS_VALUE"], str)

    # Check #N/A value
    row_na = df[df["TIME_PERIOD"] == "2003"].iloc[0]
    assert row_na["OBS_VALUE"] == "#N/A"
    assert isinstance(row_na["OBS_VALUE"], str)
