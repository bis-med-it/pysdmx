from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.reader import read_sdmx as reader
from pysdmx.io.xml.sdmx30.reader.structure import read as read_structure
from pysdmx.model import (
    Agency,
    AgencyScheme,
    Code,
    Codelist,
    Contact,
    ItemReference,
)
from pysdmx.model.dataflow import DataStructureDefinition


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


def test_agency_scheme_read(samples_folder):
    data_path = samples_folder / "agencies.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None

    assert isinstance(result[0], AgencyScheme)
    agency_scheme = result[0]
    assert agency_scheme.id == "AGENCIES"
    assert agency_scheme.name == "MD Agency Scheme"
    assert agency_scheme.agency == "MD"

    assert isinstance(agency_scheme.items[0], Agency)
    agency = agency_scheme.items[0]
    assert agency.id == "AG"
    assert agency.name == "AGENCY"
    assert agency.description == "AGENCY"
    assert (
        agency.urn
        == "urn:sdmx:org.sdmx.infomodel.base.Agency=MD:AGENCIES(1.0).AG"
    )

    assert isinstance(agency.contacts[0], Contact)
    contact = agency.contacts[0]
    assert contact.name == "CONTACT"
    assert contact.role == "ROLE"


def test_code_list_read(samples_folder):
    data_path = samples_folder / "codelists.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert len(result) == 2

    assert isinstance(result[0], Codelist)
    codelist = result[0]
    assert codelist.id == "CODELIST1"
    assert codelist.name == "Code list for Frequency (FREQ)"
    assert codelist.short_urn == "Codelist=MD:CODELIST1(1.0)"
    assert codelist.version == "1.0"

    assert len(codelist.items) == 2
    assert isinstance(codelist.items[0], Code)
    assert codelist.items[0].id == "A"
    assert codelist.items[0].name == "Annual"
    assert codelist.items[1].id == "B"
    assert codelist.items[1].name == "Daily - business week (not supported)"


def test_dataflow_structure_read(samples_folder):
    data_path = samples_folder / "dataflow_structure.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    dataflow = result[0]
    assert dataflow.id == "DATAFLOW"
    assert dataflow.name == "DATAFLOW Test"
    assert dataflow.description == "DATAFLOW Test"
    assert dataflow.short_urn == "Dataflow=MD:DATAFLOW(1.0)"
    assert dataflow.structure == "DataStructure=MD:DS(1.0)"
    assert (
        dataflow.urn == "urn:sdmx:org.sdmx.infomodel.datastructure."
        "Dataflow=MD:DATAFLOW(1.0)"
    )


def test_data_structure_read(samples_folder):
    data_path = samples_folder / "data_structure.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert isinstance(result[0], DataStructureDefinition)
    data_structure = result[0]
    assert data_structure.id == "DS"
    assert data_structure.agency == "MD"
    assert data_structure.name == "DS Test"
    assert data_structure.short_urn == "DataStructure=MD:DS(1.0)"

    attributes = data_structure.components.attributes
    assert len(attributes) == 3
    assert attributes[0].required is False
    assert attributes[0].attachment_level == "FREQ"
    assert attributes[1].required is True
    assert attributes[1].attachment_level == "O"
    assert attributes[2].required is True
    assert attributes[2].attachment_level == "D"

    dimensions = data_structure.components.dimensions
    assert len(dimensions) == 2
    assert dimensions[0].concept == ItemReference(
        sdmx_type="Concept",
        agency="MD",
        id="STANDALONE_CONCEPT_SCHEME",
        version="1.0",
        item_id="FREQ",
    )
    assert dimensions[1].concept == ItemReference(
        sdmx_type="Concept",
        agency="MD",
        id="STANDALONE_CONCEPT_SCHEME",
        version="1.0",
        item_id="TIME_PERIOD",
    )

    measures = data_structure.components.measures
    assert len(measures) == 2
    assert measures[0].id == "OBS_VALUE"
    assert measures[1].id == "OBS_VALUE1"


def test_concepts_read(samples_folder):
    data_path = samples_folder / "concepts.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    concept_scheme = result[0]
    assert concept_scheme.agency == "MD"
    assert concept_scheme.id == "STANDALONE_CONCEPT_SCHEME"
    assert concept_scheme.name == "Default Scheme"
    concepts = concept_scheme.items
    assert len(concepts) == 2


def test_concepts_codelist_read(samples_folder):
    data_path = samples_folder / "concepts_codelist.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    codelist = result[0]
    assert isinstance(codelist, Codelist)
    concepts = result[2].items
    assert len(concepts) == 1
    concept = concepts[0]
    assert concept.codes[0] == codelist.items[0]


def test_dsd_cod_concept_ref_read(samples_folder):
    data_path = samples_folder / "dsd_cod_concept_ref.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    codelist = result[1]
    code = codelist.items[0]
    concept_scheme = result[2]
    concept = concept_scheme.items[0]
    dsd = result[3]
    dimensions = dsd.components.dimensions
    dimension = dimensions[0]
    assert dimension.concept == concept
    assert dimension.enumeration[0].urn == code.urn


def test_data_structure_metadata(samples_folder):
    data_path = samples_folder / "data_structure_metadata.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None


def test_data_structure_with_link_codelist(samples_folder):
    data_path = samples_folder / "datastructure_complete_with_link.xml"
    with open(data_path, "r", encoding="utf-8") as file:
        f = file.read()
    message = reader(f, validate=True).structures
    assert message is not None


def test_data_structure_no_structure(samples_folder):
    data_path = samples_folder / "data_structure_no_structure.xml"
    with open(data_path, "r", encoding="utf-8") as file:
        f = file.read()
    with pytest.raises(
        Invalid, match="This SDMX document is not SDMX-ML 3.0 Structure."
    ):
        read_structure(f, validate=False)
