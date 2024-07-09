from pathlib import Path

import pytest

from pysdmx.errors import ClientError
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.reader import read_xml
from pysdmx.model import Contact
from pysdmx.model.message import SubmissionResult


# Test parsing SDMX Registry Interface Submission Response


@pytest.fixture()
def agency_scheme_path():
    return Path(__file__).parent / "samples" / "agencies.xml"


@pytest.fixture()
def codelist_path():
    return Path(__file__).parent / "samples" / "codelists.xml"


@pytest.fixture()
def item_scheme_path():
    return Path(__file__).parent / "samples" / "item_scheme.xml"


@pytest.fixture()
def submission_path():
    return Path(__file__).parent / "samples" / "submission_append.xml"


@pytest.fixture()
def error_304_path():
    return Path(__file__).parent / "samples" / "error_304.xml"


def test_agency_scheme_read(agency_scheme_path):
    input_str, filetype = process_string_to_read(agency_scheme_path)
    assert filetype == "xml"
    result = read_xml(input_str, validate=True)

    assert "OrganisationSchemes" in result
    agency_scheme = result["OrganisationSchemes"]
    assert len(agency_scheme) == 1
    agency_sdmx = agency_scheme["SDMX:AGENCIES(1.0)"].items[0]
    assert agency_sdmx.id == "SDMX"
    assert agency_sdmx.name == "SDMX"


def test_code_list_read(codelist_path):
    input_str, filetype = process_string_to_read(codelist_path)
    assert filetype == "xml"
    result = read_xml(input_str, validate=True)

    assert "Codelists" in result
    codelists = result["Codelists"]
    assert len(codelists) == 5
    codelist_sdmx = codelists["SDMX:CL_UNIT_MULT(1.0)"]
    assert codelist_sdmx.id == "CL_UNIT_MULT"
    assert (
        codelist_sdmx.name == "code list for the Unit Multiplier (UNIT_MULT)"
    )
    assert codelist_sdmx.items[0].id == "0"
    assert codelist_sdmx.items[0].name == "Units"


def test_item_scheme_read(item_scheme_path):
    input_str, filetype = process_string_to_read(item_scheme_path)
    assert filetype == "xml"
    result = read_xml(input_str, validate=True)

    assert "OrganisationSchemes" in result
    assert "Codelists" in result
    assert "Concepts" in result

    # Agency Scheme (OrganisationSchemes) assertions
    agency_scheme = result["OrganisationSchemes"]
    assert len(agency_scheme) == 1
    agency_sdmx = agency_scheme["SDMX:AGENCIES(1.0)"].items[0]
    assert agency_sdmx.id == "SDMX"
    assert agency_sdmx.name == "SDMX"
    agency_uis = agency_scheme["SDMX:AGENCIES(1.0)"].items[2]

    assert agency_uis.id == "UIS"
    assert isinstance(agency_uis.contacts[0], Contact)
    assert agency_uis.contacts[0].emails == ["uis.datarequests@unesco.org"]

    # Codelist
    codelists = result["Codelists"]
    assert len(codelists) == 5
    codelist_sdmx = codelists["SDMX:CL_UNIT_MULT(1.0)"]
    assert codelist_sdmx.id == "CL_UNIT_MULT"
    assert (
        codelist_sdmx.name == "code list for the Unit Multiplier (UNIT_MULT)"
    )
    assert codelist_sdmx.items[0].id == "0"
    assert codelist_sdmx.items[0].name == "Units"

    # Concept
    concepts = result["Concepts"]
    assert len(concepts) == 1
    concept_scheme_sdmx = concepts["SDMX:CROSS_DOMAIN_CONCEPTS(1.0)"]
    assert concept_scheme_sdmx.id == "CROSS_DOMAIN_CONCEPTS"
    assert concept_scheme_sdmx.name == "SDMX Cross Domain Concept Scheme"
    assert concept_scheme_sdmx.items[0].id == "COLL_METHOD"
    assert concept_scheme_sdmx.items[2].codes[0].id == "C"


def test_submission_result(submission_path):
    input_str, filetype = process_string_to_read(submission_path)
    assert filetype == "xml"
    result = read_xml(input_str, validate=True)

    short_urn_1 = "DataStructure=BIS:BIS_DER(1.0)"
    short_urn_2 = "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"

    assert short_urn_1 in result
    submission_1 = result[short_urn_1]
    assert isinstance(submission_1, SubmissionResult)
    assert submission_1.action == "Append"
    assert submission_1.short_urn == short_urn_1
    assert submission_1.status == "Success"

    assert short_urn_2 in result
    submission_2 = result[short_urn_2]
    assert isinstance(submission_2, SubmissionResult)
    assert submission_2.action == "Append"
    assert submission_2.short_urn == short_urn_2
    assert submission_2.status == "Success"


def test_error_304(error_304_path):
    input_str, filetype = process_string_to_read(error_304_path)
    assert filetype == "xml"
    with pytest.raises(ClientError) as e:
        read_xml(input_str, validate=False, mode=MessageType.Error)
    assert e.value.status == 304
    reference_title = (
        "Either no structures were submitted,\n"
        "            or the submitted structures "
        "contain no changes from the ones\n"
        "            currently stored in the system"
    )

    assert e.value.title == reference_title


def test_error_message_with_different_mode(error_304_path):
    input_str, filetype = process_string_to_read(error_304_path)
    assert filetype == "xml"
    with pytest.raises(ValueError, match="Unable to parse sdmx file as"):
        read_xml(input_str, validate=True, mode=MessageType.Submission)
