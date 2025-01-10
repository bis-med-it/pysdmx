from pathlib import Path

import pytest

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io import read_sdmx
from pysdmx.io.enums import SDMXFormat
from pysdmx.io.reader import get_datasets
from pysdmx.model import Schema


@pytest.fixture
def empty_message():
    file_path = Path(__file__).parent / "samples" / "empty_message.xml"
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def sdmx_json():
    file_path = Path(__file__).parent / "samples" / "sdmx.json"
    with open(file_path, "r") as f:
        text = f.read()
    return text


@pytest.fixture
def data_path():
    base_path = Path(__file__).parent / "samples" / "data.xml"
    return str(base_path)


@pytest.fixture
def data_csv_v1_path():
    base_path = Path(__file__).parent / "samples" / "data_v1.csv"
    return str(base_path)


@pytest.fixture
def structures_path():
    base_path = Path(__file__).parent / "samples" / "datastructure.xml"
    return str(base_path)


@pytest.fixture
def dataflow_path():
    base_path = Path(__file__).parent / "samples" / "dataflow.xml"
    return str(base_path)


def test_read_sdmx_invalid_extension():
    with pytest.raises(Invalid, match="Cannot parse input as SDMX."):
        read_sdmx(",,,,")


def test_read_sdmx_json_not_supported(sdmx_json):
    with pytest.raises(
        NotImplemented, match="JSON formats reading are not supported yet"
    ):
        read_sdmx(sdmx_json, validate=False)


def test_read_format_str():
    assert str(SDMXFormat.SDMX_ML_2_1_STRUCTURE) == "SDMX-ML 2.1 Structure"
    assert str(SDMXFormat.SDMX_ML_2_1_DATA_GENERIC) == "SDMX-ML 2.1 Generic"
    assert (
        str(SDMXFormat.SDMX_ML_2_1_DATA_STRUCTURE_SPECIFIC)
        == "SDMX-ML 2.1 StructureSpecific"
    )
    assert str(SDMXFormat.SDMX_CSV_1_0) == "SDMX-CSV 1.0"
    assert str(SDMXFormat.SDMX_CSV_2_0) == "SDMX-CSV 2.0"


def test_read_url_invalid():
    with pytest.raises(
        Invalid, match="Cannot retrieve a SDMX Message from URL"
    ):
        read_sdmx("https://www.google.com/404")


def test_read_url_valid():
    url = "https://stats.bis.org/api/v1/datastructure/BIS/BIS_DER/1.0?references=none&detail=full"
    result = read_sdmx(url)
    assert len(result.structures) == 1


def test_url_invalid_sdmx_error():
    url = "https://stats.bis.org/api/v1/datastructure/BIS/BIS_DER/1.0?references=none&detail=none"
    with pytest.raises(
        Invalid,
        match="150:",
    ):
        read_sdmx(url)


def test_empty_result(empty_message):
    with pytest.raises(Invalid, match="Empty SDMX Message"):
        read_sdmx(empty_message, validate=False)


def test_get_datasets_valid(data_path, structures_path):
    result = get_datasets(data_path, structures_path)
    assert len(result) == 1
    dataset = result[0]
    assert isinstance(dataset.structure, Schema)
    assert dataset.data is not None
    assert len(dataset.data) == 1000


def test_get_datasets_no_data_found(data_path, structures_path):
    with pytest.raises(Invalid, match="No data found in the data message"):
        get_datasets(structures_path, data_path)


def test_get_datasets_no_structure_found(data_path, structures_path):
    with pytest.raises(
        Invalid, match="No structure found in the structure message"
    ):
        get_datasets(data_path, data_path)


def test_get_datasets_no_datastructure(data_path, dataflow_path):
    result = get_datasets(data_path, dataflow_path)
    assert len(result) == 1
    assert result[0].data is not None
    assert isinstance(result[0].structure, str)


def test_get_datasets_dataflow_reference(data_csv_v1_path, dataflow_path):
    result = get_datasets(data_csv_v1_path, dataflow_path)
    assert len(result) == 1
    assert result[0].data is not None
    assert isinstance(result[0].structure, str)
    assert result[0].structure == "DataFlow=BIS:BIS_DER(1.0)"
