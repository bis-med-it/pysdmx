from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io import get_datasets, read_sdmx, write_sdmx
from pysdmx.io.csv.sdmx10.writer import write as write_csv10
from pysdmx.io.csv.sdmx20.writer import write as write_csv20
from pysdmx.io.format import Format


@pytest.fixture
def xml_data_path():
    base_path = Path(__file__).parent / "samples" / "dataset_with_nulls.xml"
    return str(base_path)


@pytest.fixture
def csv_10():
    base_path = Path(__file__).parent / "samples" / "csv_nulls_10.csv"
    with open(base_path, "rb") as f:
        return f.read().decode("utf-8")


@pytest.fixture
def csv_20():
    base_path = Path(__file__).parent / "samples" / "csv_nulls_20.csv"
    with open(base_path, "rb") as f:
        return f.read().decode("utf-8")


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


data_params = [
    (
        "data_v1_attached.csv",
        Format.DATA_SDMX_CSV_1_0_0,
    ),
    (
        "data_v1_attached.csv",
        Format.DATA_SDMX_CSV_2_0_0,
    ),
    (
        "data_v1_attached.csv",
        Format.DATA_SDMX_ML_2_1_GEN,
    ),
    (
        "data_v1_attached.csv",
        Format.DATA_SDMX_ML_2_1_STR,
    ),
    (
        "data_v1_attached.csv",
        Format.DATA_SDMX_ML_3_0,
    ),
    (
        "data_dataflow.xml",
        Format.DATA_SDMX_CSV_1_0_0,
    ),
    (
        "data.xml",
        Format.DATA_SDMX_CSV_2_0_0,
    ),
    (
        "data.xml",
        Format.DATA_SDMX_ML_2_1_GEN,
    ),
    (
        "data.xml",
        Format.DATA_SDMX_ML_2_1_STR,
    ),
    (
        "data.xml",
        Format.DATA_SDMX_ML_3_0,
    ),
]


@pytest.mark.parametrize(("filename", "output_format"), data_params)
def test_data_rwr(samples_folder, filename, output_format):
    data_path = samples_folder / filename
    structures_path = samples_folder / "dataflow_structure_children.xml"

    assert data_path.exists(), (
        f"Data file {filename} does not exist in {samples_folder}"
    )

    datasets = get_datasets(data_path, structures_path)

    output_str = write_sdmx(datasets, sdmx_format=output_format)
    datasets_2 = get_datasets(output_str, structures_path)
    assert len(datasets) == len(datasets_2), "Number of datasets mismatch"

    pd.testing.assert_frame_equal(
        datasets[0].data,
        datasets_2[0].data,
        check_dtype=False,
        check_like=True,
    )

    assert (
        datasets[0].attributes
        == datasets_2[0].attributes
        == {
            "DECIMALS": "3",
            "UNIT_MULT": "6",
            "UNIT_MEASURE": "USD",
        }
    )


data_no_structure_params = [
    (
        "data_v1.csv",
        Format.DATA_SDMX_CSV_1_0_0,
    ),
    (
        "data_v1.csv",
        Format.DATA_SDMX_CSV_2_0_0,
    ),
    (
        "data_v1.csv",
        Format.DATA_SDMX_ML_2_1_GEN,
    ),
    (
        "data_v1.csv",
        Format.DATA_SDMX_ML_2_1_STR,
    ),
    (
        "data_no_attached.xml",
        Format.DATA_SDMX_CSV_1_0_0,
    ),
    (
        "data_no_attached.xml",
        Format.DATA_SDMX_CSV_2_0_0,
    ),
    (
        "data_no_attached.xml",
        Format.DATA_SDMX_ML_2_1_GEN,
    ),
    (
        "data_no_attached.xml",
        Format.DATA_SDMX_ML_2_1_STR,
    ),
    (
        "data_no_attached.xml",
        Format.DATA_SDMX_ML_3_0,
    ),
]


@pytest.mark.parametrize(
    ("filename", "output_format"), data_no_structure_params
)
def test_data_rwr_no_structure(samples_folder, filename, output_format):
    data_path = samples_folder / filename

    assert data_path.exists(), f"Data file does not exist in {samples_folder}"

    datasets = get_datasets(data_path)

    output_str = write_sdmx(datasets, sdmx_format=Format.DATA_SDMX_CSV_2_0_0)
    datasets_2 = get_datasets(output_str)
    assert len(datasets) == len(datasets_2), "Number of datasets mismatch"

    pd.testing.assert_frame_equal(
        datasets[0].data,
        datasets_2[0].data,
        check_dtype=False,
        check_like=True,
    )


def test_read_xml_write_csv_10(xml_data_path, csv_10):
    # Read the SDMX XML data
    data = read_sdmx(xml_data_path, validate=True).data
    # Write it to SDMX CSV 1.0 format
    result = write_csv10(
        data,
    )
    assert result == csv_10


def test_read_xml_write_csv_20(xml_data_path, csv_20):
    # Read the SDMX XML data
    data = read_sdmx(xml_data_path, validate=True).data
    # Write it to SDMX CSV 2.0 format
    result = write_csv20(
        data,
    )
    assert result == csv_20


@pytest.mark.parametrize(
    "csv_format",
    [Format.DATA_SDMX_CSV_1_0_0, Format.DATA_SDMX_CSV_2_0_0],
)
def test_write_sdmx_csv_read_back(samples_folder, csv_format):
    data_path = samples_folder / "data_dataflow.xml"
    structures_path = samples_folder / "dataflow_structure_children.xml"

    datasets = get_datasets(data_path, structures_path)

    csv_output = write_sdmx(datasets, sdmx_format=csv_format)

    read_datasets = get_datasets(csv_output, structures_path)

    assert len(datasets) == len(read_datasets), "Number of datasets mismatch"

    pd.testing.assert_frame_equal(
        datasets[0].data,
        read_datasets[0].data,
        check_dtype=False,
        check_like=True,
    )

    assert (
        datasets[0].attributes
        == read_datasets[0].attributes
        == {
            "DECIMALS": "3",
            "UNIT_MULT": "6",
            "UNIT_MEASURE": "USD",
        }
    )
