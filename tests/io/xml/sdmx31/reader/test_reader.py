from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.reader import read_sdmx
from pysdmx.io.xml.sdmx31.reader.structure import read as read_structure
from pysdmx.model import (
    Codelist,
    ConceptScheme,
    NamePersonalisationScheme,
    RulesetScheme,
    TransformationScheme,
    VtlMappingScheme,
)
from pysdmx.model.dataflow import (
    Dataflow,
    DataStructureDefinition,
    ProvisionAgreement,
)


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


@pytest.mark.xml
def test_codelist_31(samples_folder):
    data_path = samples_folder / "codelist.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    codelist = result[0]
    assert isinstance(codelist, Codelist)
    assert codelist.id == "CL_AGE"
    assert codelist.agency == "SDMX"
    assert len(codelist.items) == 5


@pytest.mark.xml
def test_concept_scheme_31(samples_folder):
    data_path = samples_folder / "conceptscheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    concept_scheme = result[0]
    assert isinstance(concept_scheme, ConceptScheme)
    assert concept_scheme.id == "ECB_CONCEPTS"
    assert concept_scheme.agency == "ECB"
    assert len(concept_scheme.concepts) == 2


def test_data_dataflow_31(samples_folder):
    data_path = samples_folder / "ECB_EXR_data.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).data
    data = result[0].data
    num_rows = len(data)
    num_columns = data.shape[1]
    assert num_rows == 21
    assert num_columns == 16


@pytest.mark.xml
def test_data_structure_definition_31(samples_folder):
    data_path = samples_folder / "ECB_EXR_metadata.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
    dsd = result[0]
    assert isinstance(dsd, DataStructureDefinition)
    assert dsd.id == "ECB_EXR"
    assert dsd.agency == "ECB"
    components = dsd.components
    assert len(components.attributes) == 24
    assert len(components.data) == 31
    assert len(components.dimensions) == 6
    assert len(components.measures) == 1


def test_vtl_complete_31(samples_folder):
    data_path = samples_folder / "VTL_Sample_1.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures

    vtl_mapping = result[8]
    assert isinstance(vtl_mapping, VtlMappingScheme)
    assert vtl_mapping.id == "VTLMS1"
    assert vtl_mapping.agency == "SDMX"

    ruleset_scheme = result[9]
    assert isinstance(ruleset_scheme, RulesetScheme)
    assert ruleset_scheme.id == "RS1"
    assert ruleset_scheme.agency == "SDMX"
    assert len(ruleset_scheme.items) == 2

    name_personalisation = result[10]
    assert isinstance(name_personalisation, NamePersonalisationScheme)
    assert name_personalisation.id == "NPS1"
    assert name_personalisation.agency == "SDMX"
    assert len(name_personalisation.items) == 1

    ts_scheme = result[11]
    assert isinstance(ts_scheme, TransformationScheme)
    assert ts_scheme.id == "TS1"
    assert ts_scheme.agency == "SDMX"
    assert len(ts_scheme.items) == 2


def test_vtl_complete_3_31(samples_folder):
    data_path = samples_folder / "VTL_Sample_3.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).structures
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
    result = read_sdmx(input_str, validate=True)
    header = result.header
    assert header.receiver[0].id == "AR2"
    assert header.receiver[1].id == "UY2"
    dataflow = result.structures[0]
    assert isinstance(dataflow, Dataflow)
    assert dataflow.id == "EXR"
    assert dataflow.agency == "ECB"
    assert dataflow.structure == "DataStructure=ECB:EXR(1.0)"


def test_data_structure_no_structure(samples_folder):
    data_path = samples_folder / "data_structure_no_structure.xml"
    with open(data_path, "r", encoding="utf-8") as file:
        f = file.read()
    with pytest.raises(
        Invalid, match="This SDMX document is not SDMX-ML 3.1 Structure."
    ):
        read_structure(f, validate=False)


def test_data_no_structure_specific(samples_folder):
    from pysdmx.io.xml.sdmx31.reader.structure_specific import (
        read as read_str_spe,
    )

    data_path = samples_folder / "dataflow_no_structure_specific.xml"
    with open(data_path, "r") as f:
        text = f.read()
    with pytest.raises(
        Invalid,
        match="This SDMX document is not an SDMX-ML StructureSpecificData.",
    ):
        read_str_spe(text, validate=False)


def test_prov_agreement(samples_folder):
    data_path = samples_folder / "prov_agreement_3.1.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_1
    result = read_sdmx(input_str, validate=True).get_provision_agreements()
    assert result is not None
    prov_agreement = result[0]
    assert isinstance(prov_agreement, ProvisionAgreement)
    assert prov_agreement.id == "TEST"
    assert prov_agreement.short_urn == "ProvisionAgreement=MD:TEST(1.0)"
    assert prov_agreement.dataflow == "Dataflow=MD:TEST(1.0)"
    assert prov_agreement.provider == "DataProvider=MD:DATA_PROVIDERS(1.0).MD"


def test_read_xml_v31_nulls(samples_folder):
    data_path = samples_folder / "ECB_EXR_data_nulls.xml"
    msg = read_sdmx(data_path)
    df = msg.data[0].data

    # Check NaN value
    row_nan = df[df["TIME_PERIOD"] == "1999"].iloc[0]
    assert row_nan["OBS_VALUE"] == "NaN"
    assert isinstance(row_nan["OBS_VALUE"], str)

    # Check #N/A value
    row_na = df[df["TIME_PERIOD"] == "2000"].iloc[0]
    assert row_na["OBS_VALUE"] == "#N/A"
    assert isinstance(row_na["OBS_VALUE"], str)
