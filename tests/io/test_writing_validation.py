from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io import get_datasets, read_sdmx, write_sdmx
from pysdmx.io.format import Format


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


data_params = [
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
        "data_v1.csv",
        Format.DATA_SDMX_ML_3_0,
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


@pytest.mark.parametrize(("filename", "output_format"), data_params)
def test_data_rwr(samples_folder, filename, output_format):
    data_path = samples_folder / filename
    structures_path = samples_folder / "dataflow_structure_children.xml"

    assert (
        data_path.exists()
    ), f"Data file {filename} does not exist in {samples_folder}"

    datasets = get_datasets(data_path, structures_path)

    output_str = write_sdmx(datasets, sdmx_format=output_format)
    msg_2 = read_sdmx(output_str)
    datasets_2 = msg_2.data
    assert len(datasets) == len(datasets_2), "Number of datasets mismatch"

    pd.testing.assert_frame_equal(
        datasets[0].data,
        datasets_2[0].data,
        check_dtype=False,
        check_like=True,
    )
