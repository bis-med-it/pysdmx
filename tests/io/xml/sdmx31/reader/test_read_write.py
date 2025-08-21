from pathlib import Path

import pytest

from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.reader import read_sdmx
from pysdmx.io.xml.sdmx30.writer.structure import write as write_structure
from pysdmx.io.xml.sdmx30.writer.structure_specific import (
    write as write_str_spe,
)
from pysdmx.model import (
    Codelist,
    ConceptScheme,
    NamePersonalisationScheme,
    RulesetScheme,
    TransformationScheme,
    VtlMappingScheme,
)
from pysdmx.model.dataflow import Dataflow, DataStructureDefinition


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


def test_codelist_31(samples_folder):
    data_path = samples_folder / "codelist.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structures = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structures, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    codelist = result[0]
    assert isinstance(codelist, Codelist)


def test_concept_scheme_31(samples_folder):
    data_path = samples_folder / "conceptscheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structures = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structures, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    concept_scheme = result[0]
    assert isinstance(concept_scheme, ConceptScheme)


def test_data_dataflow_31(samples_folder):
    data_path = samples_folder / "ECB_EXR_data.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_3_1
    data = read_sdmx(input_str, validate=True).data
    write = write_str_spe(datasets=data, prettyprint=True)
    result = read_sdmx(write, validate=True).data
    read_data = result[0].data
    num_rows = len(read_data)
    num_columns = read_data.shape[1]
    assert num_rows == 21
    assert num_columns == 16


def test_data_structure_definition_31(samples_folder):
    data_path = samples_folder / "ECB_EXR_metadata.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structure = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structure, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    dsd = result[0]
    assert isinstance(dsd, DataStructureDefinition)


def test_vtl_complete_31(samples_folder):
    data_path = samples_folder / "VTL_Sample_1.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structure = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structure, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    assert result is not None
    assert isinstance(result[0], Codelist)
    assert isinstance(result[1], Codelist)
    assert isinstance(result[2], ConceptScheme)
    assert isinstance(result[3], ConceptScheme)
    assert isinstance(result[4], DataStructureDefinition)
    assert isinstance(result[5], DataStructureDefinition)
    assert isinstance(result[6], Dataflow)
    assert isinstance(result[7], Dataflow)
    assert isinstance(result[8], VtlMappingScheme)
    assert isinstance(result[9], RulesetScheme)
    assert isinstance(result[10], NamePersonalisationScheme)
    assert isinstance(result[11], TransformationScheme)


def test_vtl_complete_3_31(samples_folder):
    data_path = samples_folder / "VTL_Sample_3.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structure = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structure, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    assert len(result) == 9
    assert isinstance(result[0], Codelist)
    assert isinstance(result[1], Codelist)
    assert isinstance(result[2], ConceptScheme)
    assert isinstance(result[3], DataStructureDefinition)
    assert isinstance(result[4], DataStructureDefinition)
    assert isinstance(result[5], Dataflow)
    assert isinstance(result[6], Dataflow)
    assert isinstance(result[7], VtlMappingScheme)
    assert isinstance(result[8], TransformationScheme)


def test_dataflow_31(samples_folder):
    data_path = samples_folder / "dataflow.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    structure = read_sdmx(input_str, validate=True).structures
    write = write_structure(structures=structure, prettyprint=True)
    result = read_sdmx(write, validate=True).structures
    dataflow = result[0]
    assert isinstance(dataflow, Dataflow)
