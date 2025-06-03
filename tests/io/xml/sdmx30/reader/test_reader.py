from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.sdmx30.reader.structure_specific import read as read_str_spe


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


def test_dataflow_30(samples_folder):
    data_path = samples_folder / "data_dataflow_3.0.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_3_0
    result = read_sdmx(input_str, validate=True)
    header = result.header
    assert header.structure == {
        "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)": "AllDimensions"
    }
    assert result.data is not None
    data = result.data[0].data
    num_rows = len(data)
    num_columns = data.shape[1]
    assert num_rows == 2
    assert num_columns == 19
    print(result)


def test_datastructure_30__series(samples_folder):
    data_path = samples_folder / "data_datastructure_3.0_series.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_3_0
    result = read_sdmx(input_str, validate=True)
    header = result.header
    assert header.structure == {
        "DataStructure=BIS:BIS_CBS(1.0)": "TIME_PERIOD"
    }
    assert result.data is not None
    data = result.data[0].data
    num_rows = len(data)
    num_columns = data.shape[1]
    assert num_rows == 3
    assert num_columns == 17


def test_prov_agree_30_groups_series(samples_folder):
    data_path = samples_folder / "data_prov_agree_3.0.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_3_0
    result = read_sdmx(input_str, validate=True)
    header = result.header
    assert header.structure == {
        "ProvisionAgreement=BIS:WEBSTATS_DER_DATAFLOW(1.0)": "AllDimensions"
    }
    assert result.data is not None
    data = result.data[0].data
    num_rows = len(data)
    num_columns = data.shape[1]
    assert num_rows == 2
    assert num_columns == 2


def test_data_no_structure_specific(samples_folder):
    data_path = samples_folder / "dataflow_no_structure_specific.xml"
    with open(data_path, "r") as f:
        text = f.read()
    with pytest.raises(
        Invalid,
        match="This SDMX document is not an SDMX-ML StructureSpecificData.",
    ):
        read_str_spe(text, validate=False)
