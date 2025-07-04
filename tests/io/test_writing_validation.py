from pathlib import Path

import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.csv.sdmx10.writer import write as write_csv10
from pysdmx.io.csv.sdmx20.writer import write as write_csv20


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
