from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.csv.sdmx20.reader import read


@pytest.fixture
def data_path():
    base_path = Path(__file__).parent / "samples" / "data_v2.csv"
    return base_path


@pytest.fixture
def data_path_exception():
    base_path = Path(__file__).parent / "samples" / "data_v2_exception.csv"
    return base_path


@pytest.fixture
def data_path_no_freq():
    base_path = Path(__file__).parent / "samples" / "data_v2_no_freq_cols.csv"
    return base_path


@pytest.fixture
def data_path_action():
    base_path = Path(__file__).parent / "samples" / "data_v2_action_col.csv"
    return base_path


@pytest.fixture
def data_path_structures():
    base_path = Path(__file__).parent / "samples" / "data_v2_structures.csv"
    return base_path


@pytest.fixture
def data_path_structures_exc():
    base_path = (
        Path(__file__).parent / "samples" / "data_v2_structures_exception.csv"
    )
    return base_path


@pytest.fixture
def data_path_two_actions():
    base_path = Path(__file__).parent / "samples" / "data_v2_two_actions.csv"
    return base_path


@pytest.fixture
def data_path_three_actions():
    base_path = Path(__file__).parent / "samples" / "data_v2_three_actions.csv"
    return base_path


@pytest.fixture
def data_path_invalid_action():
    base_path = (
        Path(__file__).parent / "samples" / "data_v2_invalid_action.csv"
    )
    return base_path


def test_reading_data_v2(data_path):
    with open(data_path, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert datasets[0].short_urn == "Dataflow=BIS:BIS_DER(1.0)"
    df = datasets[0].data
    assert len(df) == 1000
    assert "STRUCTURE" not in df.columns
    assert "STRUCTURE_ID" not in df.columns
    assert "ACTION" not in df.columns
    assert len(datasets[0].attributes) == 0


def test_reading_sdmx_csv_v2(data_path):
    datasets = read_sdmx(data_path).data
    assert datasets[0].short_urn == "Dataflow=BIS:BIS_DER(1.0)"
    df = datasets[0].data
    assert len(df) == 1000
    assert "STRUCTURE" not in df.columns
    assert "STRUCTURE_ID" not in df.columns
    assert "ACTION" not in df.columns
    assert len(datasets[0].attributes) == 0


def test_reading_sdmx_csv_v2_string(data_path):
    with open(data_path, "r") as f:
        infile = f.read()
    datasets = read_sdmx(infile).data
    assert datasets[0].short_urn == "Dataflow=BIS:BIS_DER(1.0)"
    df = datasets[0].data
    assert len(df) == 1000
    assert "STRUCTURE" not in df.columns
    assert "STRUCTURE_ID" not in df.columns
    assert "ACTION" not in df.columns
    assert len(datasets[0].attributes) == 0


def test_reading_v2_exception(data_path_exception):
    with open(data_path_exception, "r") as f:
        infile = f.read()
    with pytest.raises(Invalid, match="Invalid SDMX-CSV 2.0"):
        read(infile)


def test_reading_no_freq_v2(data_path_no_freq):
    with open(data_path_no_freq, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert (
        datasets[0].short_urn
        == "Dataflow=WB:GCI(1.0):GlobalCompetitivenessIndex"
    )
    df = datasets[0].data
    assert len(df) == 7
    assert "STRUCTURE" not in df.columns
    assert "STRUCTURE_ID" not in df.columns
    assert "ACTION" not in df.columns


def test_reading_col_action(data_path_action):
    with open(data_path_action, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert datasets[0].short_urn == "Dataflow=BIS:BIS_DER(1.0)"
    df = datasets[0].data
    assert len(df) == 1000
    assert "STRUCTURE" not in df.columns
    assert "STRUCTURE_ID" not in df.columns
    assert "ACTION" not in df.columns


def test_reading_more_structures(data_path_structures):
    with open(data_path_structures, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert len(datasets) == 3
    short_urns = [ds.short_urn for ds in datasets]
    assert "Dataflow=ESTAT:DF_A(1.6.0)" in short_urns
    assert "DataStructure=ESTAT:DSD_B(1.7.0)" in short_urns
    assert "ProvisionAgreement=ESTAT:DPA_C(1.8.0)" in short_urns


def test_reading_more_structures_exception(data_path_structures_exc):
    with open(data_path_structures_exc, "r") as f:
        infile = f.read()
    with pytest.raises(Invalid, match="proper values on STRUCTURE column"):
        read(infile)


def test_reading_two_actions(data_path_two_actions):
    with open(data_path_two_actions, "r") as f:
        infile = f.read()
    datasets = read(infile)
    assert datasets[0].short_urn == "DataStructure=TEST:TEST_MD(1.0)"
    assert len(datasets[0].data) == 2


def test_reading_three_actions(data_path_three_actions):
    with open(data_path_three_actions, "r") as f:
        infile = f.read()
    with pytest.raises(
        Invalid, match="Cannot have more than one value on ACTION column"
    ):
        read(infile)


def test_reading_invalid_action(data_path_invalid_action):
    with open(data_path_invalid_action, "r") as f:
        infile = f.read()
    with pytest.raises(Invalid, match="proper values on ACTION column"):
        read(infile)
