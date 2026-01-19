import json
from datetime import datetime
from pathlib import Path
import pandas as pd

import pytest

import pysdmx
from pysdmx.errors import Invalid
from pysdmx.io import read_sdmx
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.__tokens import OBS_DIM, OBS_VALUE_ID
from pysdmx.io.xml.sdmx21.reader.error import read as read_error
from pysdmx.io.xml.sdmx21.reader.generic import read as read_generic
from pysdmx.io.xml.sdmx21.reader.structure import read as read_structure
from pysdmx.io.xml.sdmx21.reader.structure_specific import read as read_str_spe
from pysdmx.io.xml.sdmx21.reader.submission import read as read_sub
from pysdmx.io.xml.sdmx21.writer.structure_specific import write
from pysdmx.model import (
    AgencyScheme,
    Codelist,
    ConceptScheme,
    Contact,
    CustomTypeScheme,
    DataStructureDefinition,
    FromVtlMapping,
    ItemReference,
    NamePersonalisationScheme,
    ProvisionAgreement,
    Reference,
    RulesetScheme,
    ToVtlMapping,
    UserDefinedOperatorScheme,
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
    VtlMappingScheme,
)
from pysdmx.model.submission import SubmissionResult
from pysdmx.model.vtl import Ruleset, Transformation, UserDefinedOperator

# Test parsing SDMX Registry Interface Submission Response


@pytest.fixture
def agency_scheme_path():
    return Path(__file__).parent / "samples" / "agencies.xml"


@pytest.fixture
def codelist_path():
    return Path(__file__).parent / "samples" / "codelists.xml"


@pytest.fixture
def item_scheme_path():
    return Path(__file__).parent / "samples" / "item_scheme.xml"


@pytest.fixture
def submission_path():
    return Path(__file__).parent / "samples" / "submission_append.xml"


@pytest.fixture
def estat_metadata_path():
    return Path(__file__).parent / "samples" / "estat_metadata.xml"


@pytest.fixture
def estat_data_path():
    return Path(__file__).parent / "samples" / "estat_data.xml"


@pytest.fixture
def samples_folder():
    return Path(__file__).parent / "samples"


@pytest.fixture
def error_304_path():
    return Path(__file__).parent / "samples" / "error_304.xml"


@pytest.fixture
def scheme_examples_json():
    with open(
        Path(__file__).parent / "samples" / "examples.json",
        "r",
        encoding="utf-8",
    ) as file:
        return json.load(file)


@pytest.fixture
def datastructure_group():
    return Path(__file__).parent / "samples" / "datastructure_group.xml"


@pytest.fixture
def generic_groups():
    return Path(__file__).parent / "samples" / "generic_dataser_groups.xml"


@pytest.fixture
def prov_agreement_path():
    return Path(__file__).parent / "samples" / "prov_agreement_2.1.xml"


@pytest.fixture
def prov_agreement_urns_path():
    return Path(__file__).parent / "samples" / "prov_agreement_2.1_urns.xml"


@pytest.fixture
def multiple_groups_path():
    return Path(__file__).parent / "samples" / "group_merge_two_dims.xml"


@pytest.fixture
def error_str(error_304_path):
    with open(error_304_path, "r") as f:
        text = f.read()
    return text


def test_agency_scheme_read(agency_scheme_path):
    input_str, read_format = process_string_to_read(agency_scheme_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_structure(input_str, validate=True)
    assert isinstance(result[0], AgencyScheme)

    agency_scheme = result[0]
    agency_sdmx = agency_scheme.items[0]
    assert agency_sdmx.id == "SDMX"
    assert agency_sdmx.name == "SDMX"


def test_code_list_read(codelist_path):
    input_str, read_format = process_string_to_read(codelist_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    codelists = read_structure(input_str, validate=True)

    assert isinstance(codelists[0], Codelist)
    assert len(codelists) == 5
    codelist_sdmx = [cl for cl in codelists if cl.id == "CL_UNIT_MULT"][0]
    assert codelist_sdmx.id == "CL_UNIT_MULT"
    assert (
        codelist_sdmx.name == "code list for the Unit Multiplier (UNIT_MULT)"
    )
    assert codelist_sdmx.items[0].id == "0"
    assert codelist_sdmx.items[0].name == "Units"


def test_item_scheme_read(item_scheme_path):
    input_str, read_format = process_string_to_read(item_scheme_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_structure(input_str, validate=True)

    assert any(isinstance(r, Codelist) for r in result)
    assert any(isinstance(r, AgencyScheme) for r in result)
    assert any(isinstance(r, ConceptScheme) for r in result)

    # Agency Scheme (OrganisationSchemes) assertions
    agency_schemes = [r for r in result if isinstance(r, AgencyScheme)]
    assert len(agency_schemes) == 1
    agency_sdmx = agency_schemes[0].items[0]
    assert agency_sdmx.id == "SDMX"
    assert agency_sdmx.name == "SDMX"
    agency_uis = agency_schemes[0].items[2]

    assert agency_uis.id == "UIS"
    assert isinstance(agency_uis.contacts[0], Contact)
    assert agency_uis.contacts[0].emails == ["uis.datarequests@unesco.org"]

    # Codelist
    codelists = [r for r in result if isinstance(r, Codelist)]
    assert len(codelists) == 5
    codelist_sdmx = [cl for cl in codelists if cl.id == "CL_UNIT_MULT"][0]
    assert codelist_sdmx.id == "CL_UNIT_MULT"
    assert (
        codelist_sdmx.name == "code list for the Unit Multiplier (UNIT_MULT)"
    )
    assert codelist_sdmx.items[0].id == "0"
    assert codelist_sdmx.items[0].name == "Units"

    # Concept
    concepts = [r for r in result if isinstance(r, ConceptScheme)]
    assert len(concepts) == 1
    concept_scheme_sdmx = concepts[0]
    assert concept_scheme_sdmx.id == "CROSS_DOMAIN_CONCEPTS"
    assert concept_scheme_sdmx.name == "SDMX Cross Domain Concept Scheme"
    assert concept_scheme_sdmx.items[0].id == "COLL_METHOD"
    assert concept_scheme_sdmx.items[2].codes.codes[0].id == "C"


def test_submission_result(submission_path):
    input_str, read_format = process_string_to_read(submission_path)
    assert read_format == Format.REGISTRY_SDMX_ML_2_1
    result = read_sub(input_str, validate=True)

    short_urn_1 = "DataStructure=BIS:BIS_DER(1.0)"
    short_urn_2 = "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"

    submission_1 = result[0]
    assert isinstance(submission_1, SubmissionResult)
    assert submission_1.action == "Append"
    assert submission_1.short_urn == short_urn_1
    assert submission_1.status == "Success"

    submission_2 = result[1]
    assert isinstance(submission_2, SubmissionResult)
    assert submission_2.action == "Append"
    assert submission_2.short_urn == short_urn_2
    assert submission_2.status == "Success"


def test_submission_result_read_sdmx(submission_path):
    result = read_sdmx(submission_path, validate=True).submission
    assert len(result) == 2
    assert result[0].action == "Append"
    assert result[0].short_urn == "DataStructure=BIS:BIS_DER(1.0)"
    assert result[1].action == "Append"
    assert result[1].short_urn == "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"


def test_error_304(error_304_path):
    input_str, read_format = process_string_to_read(error_304_path)
    assert read_format == Format.ERROR_SDMX_ML_2_1
    with pytest.raises(Invalid) as e:
        read_error(input_str, validate=False)
    reference_title = (
        "304: Either no structures were submitted,\n"
        "            or the submitted structures "
        "contain no changes from the ones\n"
        "            currently stored in the system"
    )

    assert e.value.description == reference_title


def test_error_message_with_different_mode(agency_scheme_path):
    input_str, read_format = process_string_to_read(agency_scheme_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    with pytest.raises(
        Invalid,
        match="This SDMX document is not an SDMX-ML 2.1 Error message.",
    ):
        read_error(input_str, validate=True)


@pytest.mark.parametrize(
    "filename",
    [
        "gen_all.xml",
        "gen_ser.xml",
        "str_all.xml",
        "str_ser.xml",
        "str_ser_group.xml",
    ],
)
@pytest.mark.xml_data
def test_reading_validation(samples_folder, filename):
    data_path = samples_folder / filename
    input_str, read_format = process_string_to_read(data_path)
    assert read_format in (
        Format.DATA_SDMX_ML_2_1_GEN,
        Format.DATA_SDMX_ML_2_1_STR,
    )
    result = read_sdmx(input_str, validate=True).data
    assert result is not None
    assert len(result) == 1
    dataset = result[0]
    assert dataset.short_urn == "DataStructure=BIS:BIS_DER(1.0)"
    data = dataset.data
    assert data.shape == (1000, 20)
    assert "TIME_PERIOD" in data.columns
    assert OBS_DIM not in data.columns
    assert OBS_VALUE_ID in data.columns


@pytest.mark.parametrize(
    "filename",
    [
        "gen_all.xml",
        "gen_ser.xml",
        "str_all.xml",
        "str_ser.xml",
        "str_ser_group.xml",
    ],
)
@pytest.mark.xml_data
def test_reading_validation_read_sdmx(samples_folder, filename):
    result = read_sdmx(samples_folder / filename, validate=True).data
    assert result is not None
    data = result[0].data
    assert data.shape == (1000, 20)
    assert "TIME_PERIOD" in data.columns
    assert OBS_DIM not in data.columns
    assert OBS_VALUE_ID in data.columns


# Test reading of dataflow SDMX file
@pytest.mark.xml_data
def test_dataflow(samples_folder):
    data_path = samples_folder / "dataflow.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    result = read_sdmx(input_str, validate=True).data
    assert len(result) == 1
    dataset = result[0]
    data_dataflow = dataset.data
    num_rows = len(data_dataflow)
    num_columns = data_dataflow.shape[1]
    assert num_rows > 0
    assert num_columns > 0
    expected_num_rows = 1000
    expected_num_columns = 20
    assert num_rows == expected_num_rows
    assert num_columns == expected_num_columns
    assert "AVAILABILITY" in data_dataflow.columns
    assert "DER_CURR_LEG1" in data_dataflow.columns


def test_structure_ref_urn(samples_folder):
    data_path = samples_folder / "structure_ref_urn.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    result = read_sdmx(input_str, validate=True).data
    assert len(result) == 1
    dataset = result[0]
    assert dataset.short_urn == "DataStructure=BIS:BIS_DER(1.0)"


def test_partial_datastructure(samples_folder):
    data_path = samples_folder / "partial_datastructure.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures
    assert "DataStructure=BIS:BIS_DER(1.0)" in [ds.short_urn for ds in result]


def test_dataflow_structure(samples_folder):
    data_path = samples_folder / "dataflow_structure_no_children.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures
    assert "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)" in [
        ds.short_urn for ds in result
    ]


def test_dataflow_structure_read_sdmx(samples_folder):
    result = read_sdmx(
        samples_folder / "dataflow_structure_no_children.xml",
        validate=True,
    ).structures
    assert "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)" in [
        ds.short_urn for ds in result
    ]


def test_partial_dataflow_structure(samples_folder):
    data_path = samples_folder / "partial_dataflow_structure.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures
    assert "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)" in [
        ds.short_urn for ds in result
    ]


def test_header_structure_provision_agrement(samples_folder):
    data_path = samples_folder / "header_structure_provision_agrement.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    data = read_sdmx(input_str, validate=True).data
    assert len(data) == 1
    df = data[0].data
    assert df.shape == (1, 19)


def test_multiple_structures_in_header(samples_folder):
    data_path = samples_folder / "multiple_structures.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    data = read_sdmx(input_str, validate=True).data

    assert len(data) == 2
    assert data[0].structure == "DataStructure=MD:DS1(1.0)"
    assert data[1].structure == "DataStructure=MD:BIS_LOC_STATS(1.0)"


def test_stref_dif_strid(samples_folder):
    data_path = samples_folder / "str_dif_ref_and_ID.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    with pytest.raises(
        Exception,
        match="Dataset Structure Reference A not found in the Header",
    ):
        read_sdmx(input_str, validate=True)


def test_gen_all_no_atts(samples_folder):
    data_path = samples_folder / "gen_all_no_atts.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_GEN
    read_sdmx(input_str, validate=True)


def test_gen_ser_no_atts(samples_folder):
    data_path = samples_folder / "gen_ser_no_atts.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_GEN
    read_sdmx(input_str, validate=True)


@pytest.mark.parametrize(
    "filename",
    [
        "gen_ser_no_obs.xml",
        "str_ser_no_obs.xml",
    ],
)
def test_ser_no_obs(samples_folder, filename):
    data_path = samples_folder / filename
    input_str, read_format = process_string_to_read(data_path)
    if "gen" in filename:
        assert read_format == Format.DATA_SDMX_ML_2_1_GEN
    else:
        assert read_format == Format.DATA_SDMX_ML_2_1_STR
    result = read_sdmx(input_str, validate=True).data
    assert len(result) == 1
    df = result[0].data
    assert df.shape == (1, 16)


@pytest.mark.parametrize(
    "filename",
    [
        "gen_all.xml",
        "gen_ser.xml",
        "str_all.xml",
        "str_ser.xml",
        "str_ser_group.xml",
    ],
)
def test_chunks(samples_folder, filename):
    pysdmx.io.xml.__data_aux.READING_CHUNKSIZE = 100
    data_path = samples_folder / filename
    input_str, read_format = process_string_to_read(data_path)
    if "gen" in filename:
        assert read_format == Format.DATA_SDMX_ML_2_1_GEN
    else:
        assert read_format == Format.DATA_SDMX_ML_2_1_STR
    result = read_sdmx(input_str, validate=True).data
    assert result is not None
    assert len(result) == 1
    data = result[0].data
    num_rows = len(data)
    num_columns = data.shape[1]
    assert num_rows > 0
    assert num_columns > 0
    expected_num_rows = 1000
    expected_num_columns = 20
    assert num_rows == expected_num_rows
    assert num_columns == expected_num_columns


def test_read_write_structure_specific_all(samples_folder):
    data_path = samples_folder / "str_all.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    datasets = read_sdmx(input_str, validate=True).data
    assert datasets is not None
    assert len(datasets) == 1
    dataset = datasets[0]
    assert dataset.short_urn == "DataStructure=BIS:BIS_DER(1.0)"
    shape_read = dataset.data.shape
    assert shape_read == (1000, 20)
    result = write(datasets)
    # Check if it is well formed using validate=True
    datasets_written = read_sdmx(result, validate=True).data

    # Check we read the same data
    assert datasets_written is not None
    assert len(datasets_written) == 1
    assert datasets_written[0].short_urn == "DataStructure=BIS:BIS_DER(1.0)"
    data_written = datasets_written[0].data
    shape_written = data_written.shape
    assert shape_read == shape_written


def test_vtl_transformation_scheme(samples_folder):
    data_path = samples_folder / "transformation_scheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures

    assert result is not None
    assert len(result) == 1

    transformation_scheme = result[0]
    assert transformation_scheme.id == "TEST"
    assert transformation_scheme.name == "TEST"
    assert transformation_scheme.description == "TEST Transformation Scheme"
    assert transformation_scheme.valid_from == datetime(2024, 12, 3, 0, 0)

    assert len(transformation_scheme.items) == 2
    tr1 = transformation_scheme.items[0]
    assert isinstance(tr1, Transformation)
    assert tr1.id == "test_rule"
    assert tr1.is_persistent is True
    assert tr1.full_expression == "DS_r <- DS_1 + 1;"
    tr2 = transformation_scheme.items[1]
    assert isinstance(tr2, Transformation)
    assert tr2.id == "test_rule_2"
    assert tr2.is_persistent is False
    assert tr2.full_expression == "DS_r := DS_1 + 1;"


def test_vtl_ruleset_scheme(samples_folder, scheme_examples_json):
    data_path = samples_folder / "ruleset_scheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures

    assert result is not None
    assert len(result) == 1

    ruleset_scheme = result[0]
    expected_ruleset_scheme = scheme_examples_json["ruleset_scheme"]
    assert ruleset_scheme.id == expected_ruleset_scheme["id"]
    assert ruleset_scheme.name == expected_ruleset_scheme["name"]

    assert len(ruleset_scheme.items) == 1
    ruleset = ruleset_scheme.items[0]
    expected_ruleset = expected_ruleset_scheme["items"][0]
    assert isinstance(ruleset, Ruleset)
    assert ruleset.id == expected_ruleset["id"]
    assert ruleset.name == expected_ruleset["name"]
    assert ruleset.ruleset_scope == expected_ruleset["ruleset_scope"]
    assert ruleset.ruleset_type == expected_ruleset["ruleset_type"]
    assert ruleset.ruleset_definition == expected_ruleset["ruleset_definition"]


def test_vtl_udo_scheme(samples_folder, scheme_examples_json):
    data_path = samples_folder / "udo_scheme.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures

    assert result is not None
    assert len(result) == 1

    udo_scheme = result[0]
    expected_udo_scheme = scheme_examples_json["udo_scheme"]
    assert udo_scheme.id == expected_udo_scheme["id"]
    assert udo_scheme.name == expected_udo_scheme["name"]

    assert len(udo_scheme.items) == 1
    udo = udo_scheme.items[0]
    expected_udo = expected_udo_scheme["items"][0]
    assert isinstance(udo, UserDefinedOperator)
    assert udo.id == expected_udo["id"]
    assert udo.name == expected_udo["name"]
    assert udo.operator_definition == expected_udo["operator_definition"]


def test_vtl_full_scheme(samples_folder):
    data_path = samples_folder / "full_vtl_structure.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures
    assert result is not None
    rule_scheme = result[0]
    assert rule_scheme.agency == "MD"
    assert rule_scheme.id == "TEST_RULESET_SCHEME"
    assert rule_scheme.name == "Testing Ruleset Scheme"
    assert len(rule_scheme.items) == 1

    udo_scheme = result[1]
    assert udo_scheme.agency == "MD"
    assert udo_scheme.id == "TEST_UDO_SCHEME"
    assert udo_scheme.name == "Testing UDO Scheme"
    assert len(udo_scheme.items) == 1

    transformation_scheme = result[2]
    assert transformation_scheme.agency == "MD"
    assert transformation_scheme.id == "TEST_TS"
    assert transformation_scheme.name == "Testing TS"
    assert len(transformation_scheme.items) == 1


def test_estat_metadata(estat_metadata_path):
    input_str, sdmx_format = process_string_to_read(estat_metadata_path)
    assert sdmx_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True)
    codelists = result.get_codelists()
    concepts = result.get_concept_schemes()
    assert len(codelists) == 6
    assert len(concepts) == 1


def test_estat_data(estat_data_path):
    input_str, sdmx_format = process_string_to_read(estat_data_path)
    assert sdmx_format == Format.DATA_SDMX_ML_2_1_STR

    result = read_sdmx(input_str, validate=False).data
    assert result is not None
    assert len(result) == 1
    dataset = result[0]
    assert dataset.short_urn == "Dataflow=ESTAT:NRG_BAL_S(1.0)"
    assert len(dataset.data) == 33


def test_wrong_flavour_structure(error_str):
    with pytest.raises(Invalid):
        read_structure(error_str, validate=True)


def test_wrong_flavour_submission(error_str):
    with pytest.raises(Invalid):
        read_sub(error_str, validate=True)


def test_wrong_flavour_generic(error_str):
    with pytest.raises(Invalid):
        read_generic(error_str, validate=True)


def test_wrong_flavour_structure_specific(error_str):
    with pytest.raises(Invalid):
        read_str_spe(error_str, validate=True)


def test_structure_no_header(samples_folder):
    data_path = samples_folder / "structure_no_header.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    header = read_sdmx(input_str, validate=False).header
    assert header is None


def test_message_full(samples_folder):
    data_path = samples_folder / "message_full.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    result = read_sdmx(input_str, validate=True).header

    assert result.sender.id == "Unknown"
    assert result.sender.name == "Unknown"
    assert result.receiver[0].id == "AR2"
    assert result.receiver[1].id == "UY2"
    assert result.structure == {
        "DataStructure=BIS:BIS_DER(1.0)": "AllDimensions"
    }


def test_message_full_with_langs(samples_folder):
    data_path = samples_folder / "message_full_with_langs.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    result = read_sdmx(input_str, validate=True).header

    assert result.sender.id == "Unknown"
    assert result.sender.name == "Unknown"
    assert result.receiver[0].id == "Not_supplied"
    assert result.structure == {
        "DataStructure=BIS:BIS_DER(1.0)": "AllDimensions"
    }


def test_message_full_no_namespace(samples_folder):
    data_path = samples_folder / "message_full_no_namespace.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_GEN
    result = read_sdmx(input_str, validate=True).header
    assert result.structure == {
        "DataStructure=BIS:BIS_DER(1.0)": "AllDimensions"
    }


def test_message_full_warning(samples_folder, recwarn):
    data_path = samples_folder / "message_full_warning.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    result = read_sdmx(input_str, validate=True).header
    assert result.structure == {
        "DataStructure=BIS:BIS_DER(1.0)": "AllDimensions"
    }
    assert len(recwarn) == 1


def test_message_str_usage_urn(samples_folder):
    data_path = samples_folder / "message_str_usage_urn.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_GEN
    result = read_sdmx(input_str, validate=True).header
    assert result.structure == {
        "Dataflow=ESTAT:NAMA_10_GDP(1.0)": "TIME_PERIOD"
    }


def test_datastructure_concept_role(samples_folder):
    data_path = samples_folder / "datastructure_concept_role.xml"
    result = read_sdmx(data_path)
    dsd = result.get_data_structure_definition(
        "DataStructure=BIS:BIS_DER(1.0)"
    )
    components = dsd.components
    assert len(components) == 2
    assert components[0].id == "FREQ"


# Make test fail if a warning is raised
@pytest.mark.filterwarnings("error")
def test_header_xmlns(samples_folder):
    data_path = samples_folder / "header_xmlns.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.DATA_SDMX_ML_2_1_GEN
    result = read_sdmx(input_str, validate=True).header
    assert result.sender.id == "Disseminate_Final_DMZ"
    assert result.structure == {
        "Dataflow=OECD.SDD.STES:DSD_STES@DF_CLI(4.1)": "TIME_PERIOD"
    }


def test_vtl_data_flow_mapping_reader(samples_folder):
    data_path = samples_folder / "vtl_dataflow_mapping.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures
    assert result is not None
    assert result[0].agency == "FR1"
    assert result[0].id == "LEGAL_POP_CUBE"
    assert len(result[1].items) == 1
    items = result[1].items
    assert items[0].id == "VTLM2"
    assert items[0].dataflow_alias == "LEGAL_POP"


def test_vtl_data_flow_mapping_reader_no_dataflow(samples_folder):
    data_path = samples_folder / "vtl_dataflow_mapping_no_dataflow.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures
    assert result is not None
    assert result[0].agency == "FR1"
    assert result[0].id == "VTLMS1"
    assert len(result[0].items) == 1
    items = result[0].items
    assert items[0].id == "VTLM2"
    assert items[0].dataflow_alias == "LEGAL_POP"


def test_vtl_data_flow_mapping_reader_no_reference(samples_folder):
    data_path = samples_folder / "vtl_dataflow_mapping_no_reference.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures
    assert result is not None
    assert result[0].agency == "MD"
    assert result[0].id == "TEST"
    assert len(result[1].items) == 1
    items = result[1].items
    assert items[0].id == "VTLM2"
    assert items[0].dataflow_alias == "LEGAL_POP"


def test_transformation_scheme_references(samples_folder):
    data_path = samples_folder / "vtl_transformation_scheme_references.xml"
    msg = read_sdmx(data_path, validate=True)
    ts = msg.get_transformation_schemes()[0]
    # UDO Reference
    assert len(ts.user_defined_operator_schemes) == 1
    udo_scheme = ts.user_defined_operator_schemes[0]
    assert str(udo_scheme) == "UserDefinedOperatorScheme=MD:TEST-UDS(1.0)"
    # Ruleset Reference
    assert len(ts.ruleset_schemes) == 1
    ruleset_scheme = ts.ruleset_schemes[0]
    assert str(ruleset_scheme) == "RulesetScheme=MD:TEST-RS(1.0)"
    # VTL Mapping Scheme Reference
    assert ts.vtl_mapping_scheme is not None
    assert str(ts.vtl_mapping_scheme) == "VtlMappingScheme=MD:VMS1(1.0)"
    # Custom Type Scheme Reference
    assert ts.custom_type_scheme is not None
    assert str(ts.custom_type_scheme) == "CustomTypeScheme=MD:CTS1(1.0)"
    # Name Personalisation Scheme Reference
    assert ts.name_personalisation_scheme is not None
    assert (
        str(ts.name_personalisation_scheme)
        == "NamePersonalisationScheme=MD:NPS1(1.0)"
    )


def test_transformation_scheme_children(samples_folder):
    data_path = samples_folder / "vtl_transformation_scheme_children.xml"

    msg = read_sdmx(data_path, validate=True)
    assert len(msg.structures) == 6

    ts = msg.get_transformation_schemes()[0]
    # Custom Type Scheme
    assert isinstance(ts.custom_type_scheme, CustomTypeScheme)
    assert ts.custom_type_scheme.short_urn == "CustomTypeScheme=MD:CTS1(1.0)"
    custom_type = ts.custom_type_scheme.items[0]
    assert custom_type.id == "CT1"
    assert custom_type.vtl_scalar_type == "Test_scalar_type"
    assert custom_type.data_type == "Test_data_type"
    assert custom_type.vtl_literal_format == "Test_literal_format"
    assert custom_type.null_value == "Test_null_value"

    # Name Personalisation Scheme
    assert isinstance(
        ts.name_personalisation_scheme, NamePersonalisationScheme
    )
    assert (
        ts.name_personalisation_scheme.short_urn
        == "NamePersonalisationScheme=MD:NPS1(1.0)"
    )
    name_personalisation = ts.name_personalisation_scheme.items[0]
    assert name_personalisation.id == "NP1"
    assert name_personalisation.vtl_artefact == "TEST_VTL_ARTEFACT"
    assert name_personalisation.vtl_default_name == "TEST_DEFAULT"
    assert name_personalisation.personalised_name == "TEST_PERSONALISED"

    # VTL Mapping Scheme
    assert isinstance(ts.vtl_mapping_scheme, VtlMappingScheme)
    assert ts.vtl_mapping_scheme.short_urn == "VtlMappingScheme=MD:VMS1(1.0)"
    assert len(ts.vtl_mapping_scheme.items) == 3
    # VTL Dataflow Mapping
    vtl_dataflow_mapping = ts.vtl_mapping_scheme.items[0]
    assert isinstance(vtl_dataflow_mapping, VtlDataflowMapping)
    assert vtl_dataflow_mapping.id == "VMDataflow"
    assert vtl_dataflow_mapping.dataflow_alias == "DS_1"
    from_vtl = vtl_dataflow_mapping.from_vtl_mapping_method
    assert isinstance(from_vtl, FromVtlMapping)
    assert from_vtl.method == "Basic"
    assert len(from_vtl.from_vtl_sub_space) == 3
    assert from_vtl.from_vtl_sub_space[0] == "FREQ"
    to_vtl = vtl_dataflow_mapping.to_vtl_mapping_method
    assert isinstance(to_vtl, ToVtlMapping)
    assert to_vtl.method == "Basic"
    assert len(to_vtl.to_vtl_sub_space) == 2
    assert to_vtl.to_vtl_sub_space[0] == "FREQ"
    # VTL Codelist Mapping
    vtl_codelist_mapping = ts.vtl_mapping_scheme.items[1]
    assert isinstance(vtl_codelist_mapping, VtlCodelistMapping)
    assert isinstance(vtl_codelist_mapping.codelist, Reference)
    assert str(vtl_codelist_mapping.codelist) == "Codelist=MD:TEST_CL(1.0)"
    assert vtl_codelist_mapping.codelist_alias == "CL1"
    # VTL Concept Mapping
    vtl_concept_mapping = ts.vtl_mapping_scheme.items[2]
    assert isinstance(vtl_concept_mapping, VtlConceptMapping)
    assert isinstance(vtl_concept_mapping.concept, ItemReference)
    assert str(vtl_concept_mapping.concept) == "Concept=MD:TEST_CS(1.0).FREQ"

    # Ruleset Scheme
    assert len(ts.ruleset_schemes) == 1
    ruleset_scheme = ts.ruleset_schemes[0]
    assert isinstance(ruleset_scheme, RulesetScheme)
    assert ruleset_scheme.short_urn == "RulesetScheme=MD:TEST-RS(1.0)"
    assert isinstance(ruleset_scheme.vtl_mapping_scheme, VtlMappingScheme)
    assert (
        str(ruleset_scheme.vtl_mapping_scheme.short_urn)
        == "VtlMappingScheme=MD:VMS1(1.0)"
    )

    # User Defined Operator Scheme
    assert len(ts.user_defined_operator_schemes) == 1
    udo_scheme = ts.user_defined_operator_schemes[0]
    assert isinstance(udo_scheme, UserDefinedOperatorScheme)
    assert udo_scheme.short_urn == "UserDefinedOperatorScheme=MD:TEST-UDS(1.0)"
    assert isinstance(udo_scheme.vtl_mapping_scheme, VtlMappingScheme)
    assert len(udo_scheme.ruleset_schemes) == 1
    assert isinstance(udo_scheme.ruleset_schemes[0], RulesetScheme)
    assert udo_scheme.ruleset_schemes[0].short_urn == (
        "RulesetScheme=MD:TEST-RS(1.0)"
    )
    assert isinstance(udo_scheme.vtl_mapping_scheme, VtlMappingScheme)
    assert udo_scheme.vtl_mapping_scheme.short_urn == (
        "VtlMappingScheme=MD:VMS1(1.0)"
    )


def test_attribute_relationship_attachment_group(samples_folder):
    data_path = samples_folder / "datastructure_att_rel_attachment_group.xml"
    input_str, read_format = process_string_to_read(data_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).structures
    assert result is not None
    assert isinstance(result[0], DataStructureDefinition)
    dsd = result[0]
    assert len(dsd.groups) == 2
    assert dsd.groups[0].dimensions == ["TEST_DIM_3"]
    assert dsd.groups[1].dimensions == ["TEST_DIM_4"]
    attribute = dsd.components.attributes[0]
    assert attribute.id == "TEST"
    assert (
        attribute.attachment_level
        == "TEST_DIM_1,TEST_DIM_2,TEST_DIM_3,TEST_DIM_4"
    )


def test_datastructure_group(datastructure_group):
    input_str, read_format = process_string_to_read(datastructure_group)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
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


def test_generic_dataset_groups(generic_groups):
    input_str, read_format = process_string_to_read(generic_groups)
    assert read_format == Format.DATA_SDMX_ML_2_1_GEN
    result = read_sdmx(input_str, validate=True).data
    assert result is not None
    data = result[0].data
    num_rows = len(data)
    num_columns = data.shape[1]
    assert num_rows > 0
    assert num_columns > 0
    expected_num_rows = 176
    expected_num_columns = 19
    assert num_rows == expected_num_rows
    assert num_columns == expected_num_columns


def test_prov_agreement(prov_agreement_path):
    input_str, read_format = process_string_to_read(prov_agreement_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).get_provision_agreements()
    assert result is not None
    prov_agreement = result[0]
    assert isinstance(prov_agreement, ProvisionAgreement)
    assert prov_agreement.id == "TEST"
    assert prov_agreement.short_urn == "ProvisionAgreement=MD:TEST(1.0)"
    assert prov_agreement.dataflow == "Dataflow=MD:TEST(1.0)"
    assert prov_agreement.provider == "DataProvider=MD:DATA_PROVIDERS(1.0).MD"


def test_prov_agreement_urns(prov_agreement_urns_path):
    input_str, read_format = process_string_to_read(prov_agreement_urns_path)
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1
    result = read_sdmx(input_str, validate=True).get_provision_agreements()
    assert result is not None
    prov_agreement = result[0]
    assert isinstance(prov_agreement, ProvisionAgreement)
    assert prov_agreement.id == "TEST"
    assert prov_agreement.short_urn == "ProvisionAgreement=MD:TEST(1.0)"
    assert prov_agreement.dataflow == "Dataflow=MD:TEST(1.0)"
    assert prov_agreement.provider == "DataProvider=MD:DATA_PROVIDERS(1.0).MD"


def test_group_merge_multiple_common_columns(group_merge_two_dims_path):
    df = read_sdmx(group_merge_two_dims_path).data[0].data

    row1 = df[(df["DIM1"] == "A1") & (df["DIM2"] == "B1")]
    assert not row1.empty
    assert row1["GATTR"].iloc[0] == "G1"
    assert row1["OTHER_ATTR"].iloc[0] == "OTHER"

    row2 = df[(df["DIM1"] == "A2") & (df["DIM2"] == "B2")]
    assert not row2.empty
    assert row2["GATTR"].iloc[0] == "G2"
