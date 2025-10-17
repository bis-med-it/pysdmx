from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.reader import read_sdmx
from pysdmx.io.reader import read_sdmx as reader
from pysdmx.io.xml.sdmx30.reader.structure import read as read_structure
from pysdmx.model import (
    Agency,
    AgencyScheme,
    Code,
    Codelist,
    ConceptScheme,
    Contact,
    CustomType,
    CustomTypeScheme,
    Dataflow,
    ItemReference,
    NamePersonalisation,
    NamePersonalisationScheme,
    Reference,
    RulesetScheme,
    TransformationScheme,
    UserDefinedOperatorScheme,
    VtlDataflowMapping,
    VtlMappingScheme,
)
from pysdmx.model.dataflow import DataStructureDefinition, ProvisionAgreement
from pysdmx.util import parse_urn


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
    assert num_rows == 3
    assert num_columns == 5


def test_data_no_structure_specific(samples_folder):
    from pysdmx.io.xml.sdmx30.reader.structure_specific import (
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


@pytest.mark.xml
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


@pytest.mark.xml
def test_code_list_read(samples_folder):
    data_path = samples_folder / "codelists.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert len(result) == 1

    assert isinstance(result[0], Codelist)
    codelist = result[0]
    assert codelist.id == "CL_AGE"
    assert codelist.name == "Age"
    assert codelist.short_urn == "Codelist=SDMX:CL_AGE(1.0)"
    assert codelist.version == "1.0"
    assert codelist.is_final is True

    assert len(codelist.items) == 5
    assert isinstance(codelist.items[0], Code)
    assert codelist.items[0].id == "Y"
    assert codelist.items[0].name == "Year(s)"
    assert codelist.items[1].id == "M"
    assert codelist.items[1].name == "Month(s)"


def test_codelist_read_draft(samples_folder):
    data_path = samples_folder / "codelist_draft_version.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert len(result) == 1

    assert isinstance(result[0], Codelist)
    codelist: Codelist = result[0]
    assert codelist.id == "CL_DRAFT"
    assert codelist.name == "Draft Codelist"
    assert codelist.short_urn == "Codelist=MD:CL_DRAFT(1.0.0-Draft)"
    assert codelist.version == "1.0.0-Draft"
    assert codelist.is_final is False
    assert len(codelist.codes) == 0


def test_dataflow_read_final(samples_folder):
    data_path = samples_folder / "dataflow_final_version.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert len(result) == 1

    assert isinstance(result[0], Dataflow)
    dataflow: Dataflow = result[0]
    assert dataflow.id == "NAMAIN_IDC_N"
    assert dataflow.agency == "SDMX"
    assert dataflow.name == "NAMAIN_IDC_N df"
    assert dataflow.short_urn == "Dataflow=SDMX:NAMAIN_IDC_N(1.0)"
    assert dataflow.version == "1.0"
    assert dataflow.is_final is True
    assert dataflow.is_external_reference is False
    assert "DataStructure=ESTAT:NA_MAIN(1.6)" in dataflow.structure


def test_value_list_read(samples_folder):
    data_path = samples_folder / "valuelist.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert len(result) == 1
    assert isinstance(result[0], Codelist)
    codelist = result[0]
    assert codelist.id == "VL_CURRENCY_SYMBOL"
    assert codelist.name == "Currency Symbol"
    assert codelist.short_urn == "ValueList=EXAMPLE:VL_CURRENCY_SYMBOL(1.0)"
    assert codelist.sdmx_type == "valuelist"


@pytest.mark.xml
def test_dataflow_structure_read(samples_folder):
    data_path = samples_folder / "dataflow_structure.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    dataflow = result[0]
    assert dataflow.id == "EXR"
    assert dataflow.name == "ECB Exchange Rates"
    assert (
        dataflow.description == "ECB Exchange Rates - example of "
        "a 'non-country-specific' data source"
    )
    assert dataflow.short_urn == "Dataflow=ECB:EXR(1.0)"
    assert dataflow.structure == "DataStructure=ECB:EXR(1.0)"
    assert (
        dataflow.urn
        == "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=ECB:EXR(1.0)"
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


def test_concept_scheme_read(samples_folder):
    data_path = samples_folder / "conceptscheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert isinstance(result[0], ConceptScheme)
    concept_scheme = result[0]
    assert concept_scheme.id == "ECB_CONCEPTS"
    assert concept_scheme.name == "ECB concepts"
    assert concept_scheme.short_urn == "ConceptScheme=ECB:ECB_CONCEPTS(1.0)"
    assert len(concept_scheme.items) == 342


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
    assert concept.codes.items[0] == codelist.items[0]


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
    assert dimension.concept == parse_urn(concept.urn)
    assert dimension.enumeration.items[0].urn == code.urn


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


def test_transformation_scheme_read(samples_folder):
    data_path = samples_folder / "transformation_scheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    transformation_scheme = result[0]
    assert transformation_scheme.id == "TEST"
    assert transformation_scheme.name == "TEST"
    assert transformation_scheme.description == "TEST"
    assert (
        transformation_scheme.short_urn
        == "TransformationScheme=SDMX:TEST(1.0)"
    )
    tranformations = transformation_scheme.items
    assert len(tranformations) == 2
    assert tranformations[0].id == "test_trans"
    assert tranformations[0].is_persistent is True
    assert tranformations[0].full_expression == "DS_r <- DS_1 + 1;"
    assert tranformations[1].id == "test_trans2"
    assert tranformations[1].is_persistent is False
    assert tranformations[1].full_expression == "DS_r := DS_1 + 1;"
    ruleset_schemes = transformation_scheme.ruleset_schemes
    assert ruleset_schemes[0] == Reference(
        sdmx_type="RulesetScheme",
        agency="MD",
        id="TEST_RULE_SCHEME",
        version="1.0",
    )
    udo_schemes = transformation_scheme.user_defined_operator_schemes
    assert udo_schemes[0] == Reference(
        sdmx_type="UserDefinedOperatorScheme",
        agency="MD",
        id="TEST_UDO_SCHEME",
        version="1.0",
    )


def test_ruleset_scheme_read(samples_folder):
    data_path = samples_folder / "ruleset_scheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    ruleset_scheme = result[0]
    assert ruleset_scheme.id == "TEST_RULESET_SCHEME"
    assert ruleset_scheme.name == "Testing Ruleset Scheme"
    assert (
        ruleset_scheme.short_urn == "RulesetScheme=MD:TEST_RULESET_SCHEME(1.0)"
    )
    rulesets = ruleset_scheme.items
    assert len(rulesets) == 1
    assert rulesets[0].id == "TEST_DATAPOINT_RULESET"
    assert rulesets[0].name == "Testing Datapoint Ruleset"
    assert rulesets[0].ruleset_scope == "variable"
    assert rulesets[0].ruleset_type == "datapoint"


def test_udo_scheme_read(samples_folder):
    data_path = samples_folder / "udo_scheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    udo_scheme = result[0]
    assert udo_scheme.id == "TEST_UDO_SCHEME"
    assert udo_scheme.name == "Testing UDO Scheme"
    assert (
        udo_scheme.short_urn
        == "UserDefinedOperatorScheme=MD:TEST_UDO_SCHEME(1.0)"
    )
    udos = udo_scheme.items
    assert len(udos) == 1
    assert udos[0].id == "TEST_UDO"
    assert udos[0].name == "UDO Testing"
    ruleset_schemes = udo_scheme.ruleset_schemes
    assert len(ruleset_schemes) == 1
    assert ruleset_schemes[0] == Reference(
        sdmx_type="RulesetScheme",
        agency="MD",
        id="TEST_RULESET_SCHEME",
        version="1.0",
    )


def test_vtl_scheme_references_read(samples_folder):
    data_path = samples_folder / "vtl_scheme_references.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    udo_scheme = result[1]
    assert udo_scheme.id == "TEST_UDO_SCHEME"
    assert udo_scheme.name == "Testing UDO Scheme"
    udo_rule_schemes = udo_scheme.ruleset_schemes
    assert len(udo_rule_schemes) == 1
    assert udo_rule_schemes[0].id == "TEST_RULESET_SCHEME"
    assert udo_rule_schemes[0].agency == "MD"
    assert udo_rule_schemes[0].version == "1.0"
    assert (
        udo_rule_schemes[0].short_urn
        == "RulesetScheme=MD:TEST_RULESET_SCHEME(1.0)"
    )
    transformation_scheme = result[2]
    assert transformation_scheme.id == "TEST"
    assert transformation_scheme.name == "TEST"
    trans_rule_schemes = transformation_scheme.ruleset_schemes
    assert len(trans_rule_schemes) == 1
    assert trans_rule_schemes[0].id == "TEST_RULESET_SCHEME"
    assert trans_rule_schemes[0].agency == "MD"
    assert trans_rule_schemes[0].version == "1.0"
    assert (
        trans_rule_schemes[0].short_urn
        == "RulesetScheme=MD:TEST_RULESET_SCHEME(1.0)"
    )
    trans_udo_schemes = transformation_scheme.user_defined_operator_schemes
    assert len(trans_udo_schemes) == 1
    assert trans_udo_schemes[0].id == "TEST_UDO_SCHEME"
    assert trans_udo_schemes[0].agency == "MD"
    assert trans_udo_schemes[0].version == "1.0"
    assert (
        trans_udo_schemes[0].short_urn
        == "UserDefinedOperatorScheme=MD:TEST_UDO_SCHEME(1.0)"
    )


def test_vtl_mapping_read(samples_folder):
    data_path = samples_folder / "vtlmapping.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert len(result) == 3
    # Vtl Mapping Scheme
    assert isinstance(result[0], VtlMappingScheme)
    vtl_mapping_scheme = result[0]
    assert vtl_mapping_scheme.id == "VTLMS1"
    assert vtl_mapping_scheme.name == "Test Vtl Mapping Scheme"
    assert vtl_mapping_scheme.short_urn == "VtlMappingScheme=MD:VTLMS1(1.0)"
    assert isinstance(vtl_mapping_scheme.items[0], VtlDataflowMapping)
    vtl_dataflow = vtl_mapping_scheme.items[0]
    assert vtl_dataflow.id == "VTLM1"
    assert vtl_dataflow.name == "Test Vtl Mapping"
    # Name Personalisation Scheme
    assert isinstance(result[1], NamePersonalisationScheme)
    name_personalisation_scheme = result[1]
    assert name_personalisation_scheme.id == "NPS1"
    assert (
        name_personalisation_scheme.name == "Test Name Personalisation Scheme"
    )
    assert (
        name_personalisation_scheme.short_urn
        == "NamePersonalisationScheme=MD:NPS1(1.0)"
    )
    assert isinstance(
        name_personalisation_scheme.items[0], NamePersonalisation
    )
    name_personalisation = name_personalisation_scheme.items[0]
    assert name_personalisation.id == "NP1"
    assert name_personalisation.name == "Test Name Personalisation"
    assert name_personalisation.vtl_artefact == "TEST_VTL_ARTEFACT"
    assert name_personalisation.vtl_default_name == "TEST_DEFAULT"
    # Custom Type Scheme
    assert isinstance(result[2], CustomTypeScheme)
    custom_type_scheme = result[2]
    assert custom_type_scheme.id == "CTS1"
    assert custom_type_scheme.name == "Test Custom Type Scheme"
    assert custom_type_scheme.short_urn == "CustomTypeScheme=MD:CTS1(1.0)"
    assert isinstance(custom_type_scheme.items[0], CustomType)
    custom_type = custom_type_scheme.items[0]
    assert custom_type.id == "CT1"
    assert custom_type.name == "Test Custom Type"
    assert custom_type.null_value == "Test_literal_format"
    assert custom_type.output_format == "Test_null_value"
    assert custom_type.vtl_literal_format == "Test_output_format"
    assert custom_type.vtl_scalar_type == "Test_scalar_type"


def test_vtl_mapping_no_sub_space_read(samples_folder):
    data_path = samples_folder / "vtlmapping_no_sub_space.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    vtl_mapping_Scheme = result[0]
    assert len(vtl_mapping_Scheme.items) == 2
    items = vtl_mapping_Scheme.items
    assert isinstance(items[0], VtlDataflowMapping)
    item1 = items[0]
    assert item1.name == "VTL Mapping #1"
    assert len(item1.from_vtl_mapping_method.from_vtl_sub_space) == 0
    item2 = items[1]
    assert item2.name == "VTL Mapping #2"
    assert len(item2.to_vtl_mapping_method.to_vtl_sub_space) == 0
    assert result is not None


def test_vtl_complete_read(samples_folder):
    data_path = samples_folder / "vtl_complete.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert len(result) == 6

    assert isinstance(result[1], RulesetScheme)
    ruleset_scheme = result[1]
    rule_vtl_mapping = ruleset_scheme.vtl_mapping_scheme
    assert rule_vtl_mapping.id == "VMS1"
    assert rule_vtl_mapping.name == "Test VTL Mapping Scheme"
    assert rule_vtl_mapping.short_urn == "VtlMappingScheme=MD:VMS1(1.0)"

    assert isinstance(result[2], UserDefinedOperatorScheme)
    udo_scheme = result[2]
    udo_vtl_mapping = udo_scheme.vtl_mapping_scheme
    assert udo_vtl_mapping.id == "VMS1"
    assert udo_vtl_mapping.name == "Test VTL Mapping Scheme"
    assert udo_vtl_mapping.short_urn == "VtlMappingScheme=MD:VMS1(1.0)"

    assert isinstance(result[5], TransformationScheme)
    transformation_scheme = result[5]
    trans_custom_Scheme = transformation_scheme.custom_type_scheme
    assert trans_custom_Scheme.id == "CTS1"
    assert trans_custom_Scheme.name == "Test Custom Type Scheme"
    assert trans_custom_Scheme.short_urn == "CustomTypeScheme=MD:CTS1(1.0)"
    trans_name_personalisation_scheme = (
        transformation_scheme.name_personalisation_scheme
    )
    assert trans_name_personalisation_scheme.id == "NPS1"
    assert (
        trans_name_personalisation_scheme.name
        == "Test Name Personalisation Scheme"
    )
    assert (
        trans_name_personalisation_scheme.short_urn
        == "NamePersonalisationScheme=MD:NPS1(1.0)"
    )
    trans_vtl_mapping_scheme = transformation_scheme.vtl_mapping_scheme
    assert trans_vtl_mapping_scheme.id == "VMS1"
    assert trans_vtl_mapping_scheme.name == "Test VTL Mapping Scheme"
    assert (
        trans_vtl_mapping_scheme.short_urn == "VtlMappingScheme=MD:VMS1(1.0)"
    )


def test_vtl_sample_no_code(samples_folder):
    data_path = samples_folder / "VTL_Sample_1.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_structure(input_str, validate=True)
    assert result is not None
    assert len(result) == 12
    assert isinstance(result[0], Codelist)
    codelist = result[0]
    assert len(codelist.items) == 0


def test_datastructure_group(samples_folder):
    data_path = samples_folder / "datastructure_group.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_sdmx(input_str, validate=True).structures
    dsd = result[0]
    assert isinstance(dsd, DataStructureDefinition)
    group = dsd.groups
    assert group[0].id == "Sibling"
    assert group[0].dimensions == [
        "L_MEASURE",
        "L_REP_CTY",
        "CBS_BANK_TYPE",
        "CBS_BASIS",
        "L_POSITION",
        "L_INSTR",
        "REM_MATURITY",
        "CURR_TYPE_BOOK",
        "L_CP_SECTOR",
        "L_CP_COUNTRY",
    ]
    attribute_1 = dsd.components.attributes[4]
    assert attribute_1.attachment_level == ",".join(group[0].dimensions)
    attribute_2 = dsd.components.attributes[8]
    assert attribute_2.attachment_level == ",".join(group[0].dimensions)


def test_value_list_enum(samples_folder):
    data_path = samples_folder / "valuelist_enum.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_sdmx(input_str, validate=True)
    # Get structure
    structure = result.structures
    assert structure is not None
    # Get attributes to check the enumeration
    attributes = structure[2].components.attributes
    enumeration = attributes[0].enumeration
    # Assertions for the enumeration
    assert enumeration is not None
    assert enumeration.sdmx_type == "valuelist"
    assert enumeration.id == "VL_TEST"
    # Get the valueslist from the message
    # and check it is the same as the enumeration
    valuelist = result.get_value_lists()[0]
    assert valuelist.short_urn == "ValueList=MD:VL_TEST(1.0)"
    assert valuelist.sdmx_type == enumeration.sdmx_type
    assert valuelist.id == enumeration.id
    assert valuelist.items == enumeration.items


def test_prov_agreement(samples_folder):
    data_path = samples_folder / "prov_agreement_3.0.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_3_0
    result = read_sdmx(input_str, validate=True).get_provision_agreements()
    assert result is not None
    prov_agreement = result[0]
    assert isinstance(prov_agreement, ProvisionAgreement)
    assert prov_agreement.id == "TEST"
    assert prov_agreement.short_urn == "ProvisionAgreement=MD:TEST(1.0)"
    assert prov_agreement.dataflow == "Dataflow=MD:TEST(1.0)"
    assert prov_agreement.provider == "DataProvider=MD:DATA_PROVIDERS(1.0).MD"
