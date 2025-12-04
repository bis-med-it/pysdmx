from pathlib import Path

import pandas as pd
import pytest

from pysdmx.io import get_datasets, read_sdmx, write_sdmx
from pysdmx.io.csv.sdmx10.writer import write as write_csv10
from pysdmx.io.csv.sdmx20.writer import write as write_csv20
from pysdmx.io.format import Format
from pysdmx.model.concept import Concept
from pysdmx.model.dataflow import Component, Components, Role, Schema


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


@pytest.fixture
def schema():
    return Schema(
        context="dataflow",
        agency="Short",
        id="Urn",
        version="1.0",
        components=Components(
            [
                Component(
                    id="A",
                    required=False,
                    role=Role.MEASURE,
                    concept=Concept(id="A"),
                )
            ]
        ),
    )


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
    structures_path = samples_folder / "dataflow_structure_children.xml"

    assert data_path.exists(), f"Data file does not exist in {samples_folder}"

    datasets = get_datasets(data_path, structures_path)

    output_str = write_sdmx(datasets, sdmx_format=Format.DATA_SDMX_CSV_2_0_0)
    datasets_2 = get_datasets(output_str, structures_path)
    assert len(datasets) == len(datasets_2), "Number of datasets mismatch"

    pd.testing.assert_frame_equal(
        datasets[0].data,
        datasets_2[0].data,
        check_dtype=False,
        check_like=True,
    )


def test_read_xml_write_csv_10(xml_data_path, csv_10, schema):
    # Read the SDMX XML data
    data = read_sdmx(xml_data_path, validate=True).data
    for ds in data:
        ds.structure = schema

    # Write it to SDMX CSV 1.0 format
    result = write_csv10(
        data,
    )
    assert result == csv_10


def test_read_xml_write_csv_20(xml_data_path, csv_20, schema):
    # Read the SDMX XML data
    data = read_sdmx(xml_data_path, validate=True).data
    for ds in data:
        ds.structure = schema

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


@pytest.mark.parametrize(
    "format_",
    [
        Format.DATA_SDMX_ML_2_1_STR,
        Format.DATA_SDMX_ML_2_1_GEN,
        Format.DATA_SDMX_ML_3_0,
        Format.DATA_SDMX_ML_3_1,
        Format.DATA_SDMX_CSV_1_0_0,
        Format.DATA_SDMX_CSV_2_0_0,
        Format.DATA_SDMX_CSV_2_1_0,
    ],
)
def test_attributes_preservation(samples_folder, format_):
    csv_path = samples_folder / "csv_mixed_attributes.csv"
    dsd_path = samples_folder / "datastructure_mixed_attributes.xml"

    datasets = get_datasets(csv_path, dsd_path)
    orig_data = datasets[0].data

    val_2020_req = orig_data.at[0, "ATT_REQ"]
    # Verify required empty attribute is read as empty
    assert val_2020_req == "", "Input 2020 ATT_REQ should be empty"

    val_2021_opt = orig_data.at[1, "ATT_OPT"]
    # Verify optional empty attribute is read as empty
    assert val_2021_opt == "", "Input 2021 ATT_OPT should be empty"

    val_2022_opt = orig_data.at[2, "ATT_OPT"]
    # 'Nan' is read as literal text
    assert val_2022_opt == "Nan", (
        f"Input 2022 ATT_OPT should be text 'Nan', got {val_2022_opt!r}"
    )

    val_2023_opt = orig_data.at[3, "ATT_OPT"]
    # '#N/A' is read as literal text
    assert val_2023_opt == "#N/A", (
        f"Input 2023 ATT_OPT should be text '#N/A', got {val_2023_opt!r}"
    )

    val_2024_obs = orig_data.at[4, "OBS_VALUE"]
    # 'NaN' in numeric field is read as literal text
    assert val_2024_obs == "NaN", (
        f"Input 2024 OBS_VALUE should be literal string 'NaN' (strict reader)."
        f" Got: {val_2024_obs!r}"
    )

    # Roundtrip
    output_str = write_sdmx(datasets, sdmx_format=format_)
    datasets_2 = get_datasets(output_str, dsd_path)

    new_data = datasets_2[0].data

    assert "ATT_OPT_EMPTY" not in new_data.columns, (
        f"ATT_OPT_EMPTY (all empty) should be dropped in {format_}"
    )

    # Required attributes must be present
    assert "ATT_REQ" in new_data.columns, (
        "ATT_REQ (required) must be present in output"
    )
    val_req_out = new_data.at[0, "ATT_REQ"]
    # Required attribute must be explicitly preserved as empty string
    assert val_req_out == "", (
        "Output 2020 ATT_REQ (required) must be preserved as empty string"
    )

    val_opt_2021 = new_data.at[1, "ATT_OPT"]
    # Optional attribute (Implicit Null) Must remain empty
    assert val_opt_2021 == "", (
        "Output 2021 ATT_OPT (Implicit Null) should be empty"
    )

    val_opt_2022 = new_data.at[2, "ATT_OPT"]
    # Text 'Nan' in String attribute must survive roundtrip as valid text
    assert val_opt_2022 == "Nan", (
        f"Output 2022 ATT_OPT should preserve text 'Nan'."
        f" Got: {val_opt_2022!r}"
    )

    val_opt_2023 = new_data.at[3, "ATT_OPT"]
    # Explicit marker '#N/A' in String and must survive roundtrip as is
    assert val_opt_2023 == "#N/A", (
        f"Output 2023 ATT_OPT must preserve explicit '#N/A'."
        f" Got: {val_opt_2023!r}"
    )

    val_obs_2024 = new_data.at[4, "OBS_VALUE"]
    # Input text 'NaN' returns as text 'NaN'
    assert val_obs_2024 == "NaN", (
        f"Output 2024 OBS_VALUE should be preserved as text 'NaN'."
        f" Got: {val_obs_2024!r}"
    )
