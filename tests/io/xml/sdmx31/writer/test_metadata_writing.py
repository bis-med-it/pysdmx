"""Tests for writing SDMX-ML 3.1 reference metadata (GenericMetadata)."""

from pathlib import Path

import pytest

from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.reader import read_sdmx
from pysdmx.io.xml.sdmx31.writer.metadata import write


@pytest.fixture
def samples_folder():
    return Path(__file__).parent.parent / "reader" / "samples"


@pytest.mark.xml
def test_generic_metadata_round_trip_31(samples_folder):
    data_path = samples_folder / "generic_metadata.xml"
    reports = read_sdmx(str(data_path), validate=True).get_reports()
    result = write(reports, prettyprint=True)
    assert "<mes:GenericMetadata" in result
    assert "schemas/v3_1/" in result
    # In SDMX-ML 3.1 each <Value> holds a single value: a list expands into
    # repeated <Attribute> elements (one <Value> each).
    assert result.count('<metadata:Attribute id="EMAIL">') == 2
    _, read_format = process_string_to_read(result)
    assert read_format == Format.REFMETA_SDMX_ML_3_1
    re_read = read_sdmx(result, validate=True).get_reports()
    assert list(re_read) == list(reports)


@pytest.mark.xml
def test_generic_metadata_write_sdmx_31(samples_folder):
    from pysdmx.io import write_sdmx

    data_path = samples_folder / "generic_metadata.xml"
    reports = read_sdmx(str(data_path), validate=True).get_reports()
    result = write_sdmx(reports, Format.REFMETA_SDMX_ML_3_1)
    re_read = read_sdmx(result, validate=True).get_reports()
    assert list(re_read) == list(reports)


@pytest.mark.xml
def test_generic_metadata_output_path_31(samples_folder, tmp_path):
    data_path = samples_folder / "generic_metadata.xml"
    reports = read_sdmx(str(data_path), validate=True).get_reports()
    output_path = str(tmp_path / "out_31.xml")
    result = write(reports, output_path=output_path)
    assert result is None
    re_read = read_sdmx(output_path, validate=True).get_reports()
    assert list(re_read) == list(reports)
