from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io import get_datasets, write_sdmx
from pysdmx.io.format import Format


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

    assert (
        data_path.exists()
    ), f"Data file {filename} does not exist in {samples_folder}"

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
