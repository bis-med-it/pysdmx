from datetime import datetime
from pathlib import Path

import pytest

import pysdmx
from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml import read
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.writer import writer as write_xml
from pysdmx.model import Contact, Codelist, ConceptScheme, Dataflow
from pysdmx.model.__base import ItemScheme
from pysdmx.model.message import SubmissionResult
from pysdmx.model.vtl import Transformation, TransformationScheme


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
def samples_folder():
    return Path(__file__).parent / "samples"


@pytest.fixture
def error_304_path():
    return Path(__file__).parent / "samples" / "error_304.xml"


def test_agency_scheme_read(agency_scheme_path):
    result = read(agency_scheme_path, validate=True)

    agency_scheme = result[0]
    assert isinstance(agency_scheme, ItemScheme)
    agency_sdmx = agency_scheme.items[0]
    assert agency_sdmx.id == "SDMX"
    assert agency_sdmx.name == "SDMX"


def test_code_list_read(codelist_path):
    result = read(codelist_path, validate=True)

    assert len(result) == 5
    assert all(isinstance(item, Codelist) for item in result)
    codelist_sdmx = result[-1]
    assert isinstance(codelist_sdmx, Codelist)
    assert codelist_sdmx.id == "CL_UNIT_MULT"
    assert (
        codelist_sdmx.name == "code list for the Unit Multiplier (UNIT_MULT)"
    )
    assert codelist_sdmx.items[0].id == "0"
    assert codelist_sdmx.items[0].name == "Units"


def test_item_scheme_read(item_scheme_path):
    result = read(item_scheme_path, validate=True)

    assert any(isinstance(item, ItemScheme) for item in result)
    assert any(isinstance(item, Codelist) for item in result)
    assert any(isinstance(item, ConceptScheme) for item in result)

    # Agency Scheme (OrganisationSchemes) assertions
    # que pille el primer item scheme de la lista
    agency_scheme = next(e for e in result if isinstance(e, ItemScheme))
    agency_sdmx = agency_scheme.items[0]
    assert agency_sdmx.id == "SDMX"
    assert agency_sdmx.name == "SDMX"
    agency_uis = agency_scheme.items[2]

    assert agency_uis.id == "UIS"
    assert isinstance(agency_uis.contacts[0], Contact)
    assert agency_uis.contacts[0].emails == ["uis.datarequests@unesco.org"]

    # Codelist
    codelists = [cl for cl in result if isinstance(cl, Codelist)]
    assert len(codelists) == 5
    codelist_sdmx = next(cl for cl in codelists if cl.id == "CL_UNIT_MULT")
    assert codelist_sdmx.id == "CL_UNIT_MULT"
    assert (
        codelist_sdmx.name == "code list for the "
        "Unit Multiplier (UNIT_MULT)"
    )
    assert codelist_sdmx.items[0].id == "0"
    assert codelist_sdmx.items[0].name == "Units"

    # Concept
    concept_scheme_sdmx = next(cs for cs in result if isinstance(cs, ConceptScheme))
    assert concept_scheme_sdmx.id == "CROSS_DOMAIN_CONCEPTS"
    assert concept_scheme_sdmx.name == "SDMX Cross Domain Concept Scheme"
    assert concept_scheme_sdmx.items[0].id == "COLL_METHOD"
    assert concept_scheme_sdmx.items[2].codes[0].id == "C"


def test_submission_result(submission_path):
    result = read(submission_path, validate=True)

    short_urn_1 = "DataStructure=BIS:BIS_DER(1.0)"
    short_urn_2 = "Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)"

    assert any(short_urn_1 == sm.short_urn for sm in result)
    submission_1 = next(sm for sm in result if sm.short_urn == short_urn_1)
    assert isinstance(submission_1, SubmissionResult)
    assert submission_1.action == "Append"
    assert submission_1.short_urn == short_urn_1
    assert submission_1.status == "Success"

    assert any(short_urn_2 == sm.short_urn for sm in result)
    submission_2 = next(sm for sm in result if sm.short_urn == short_urn_2)
    assert isinstance(submission_2, SubmissionResult)
    assert submission_2.action == "Append"
    assert submission_2.short_urn == short_urn_2
    assert submission_2.status == "Success"


def test_error_304(error_304_path):
    with pytest.raises(Invalid) as e:
        read(error_304_path, validate=False)
    reference_title = (
        "304: Either no structures were submitted,\n"
        "            or the submitted structures "
        "contain no changes from the ones\n"
        "            currently stored in the system"
    )

    assert e.value.description == reference_title


# def test_error_message_with_different_mode(error_304_path):
#     with pytest.raises(Invalid, match="Unable to parse sdmx file as"):
#         read(error_304_path, validate=True)


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
def test_reading_validation(samples_folder, filename):
    data_path = samples_folder / filename
    result = read(data_path, validate=True)
    assert result is not None
    data = next(ds for ds in result if ds.short_urn == 'DataStructure=BIS:BIS_DER(1.0)').data
    assert data.shape == (1000, 20)


# Test reading of dataflow SDMX file
def test_dataflow(samples_folder):
    data_path = samples_folder / "dataflow.xml"
    result = read(data_path, validate=True)
    assert any(isinstance(item, PandasDataset) for item in result)
    data_dataflow = next(df for df in result if df.short_urn == 'DataFlow=BIS:WEBSTATS_DER_DATAFLOW(1.0)').data
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
    result = read(data_path, validate=True)
    assert any(e.short_urn == 'DataStructure=BIS:BIS_DER(1.0)' for e in result)


def test_partial_datastructure(samples_folder):
    data_path = samples_folder / "partial_datastructure.xml"
    result = read(data_path, validate=True)
    assert (e.short_urn == 'DataStructure=BIS:BIS_DER(1.0)' for e in result)


def test_dataflow_structure(samples_folder):
    data_path = samples_folder / "dataflow_structure.xml"
    result = read(data_path, validate=True)
    assert (e.short_urn == 'Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)' for e in result)


def test_partial_dataflow_structure(samples_folder):
    data_path = samples_folder / "partial_dataflow_structure.xml"
    result = read(data_path, validate=True)
    assert (e.short_urn == 'Dataflow=BIS:WEBSTATS_DER_DATAFLOW(1.0)' for e in result)


def test_header_structure_provision_agrement(samples_folder):
    data_path = samples_folder / "header_structure_provision_agrement.xml"
    with pytest.raises(NotImplemented, match="ProvisionAgrement"):
        read(data_path, validate=True)


def test_stref_dif_strid(samples_folder):
    data_path = samples_folder / "str_dif_ref_and_ID.xml"
    with pytest.raises(
        Exception,
        match="Cannot find the structure reference of this dataset:A",
    ):
        read(data_path, validate=True)


def test_gen_all_no_atts(samples_folder):
    data_path = samples_folder / "gen_all_no_atts.xml"
    read(data_path, validate=True)


def test_gen_ser_no_atts(samples_folder):
    data_path = samples_folder / "gen_ser_no_atts.xml"
    read(data_path, validate=True)


@pytest.mark.parametrize(
    "filename",
    [
        "gen_ser_no_obs.xml",
        "str_ser_no_obs.xml",
    ],
)
def test_ser_no_obs(samples_folder, filename):
    data_path = samples_folder / filename
    result = read(data_path, validate=True)
    data = next(ds for ds in result if ds.short_urn == 'DataStructure=BIS:BIS_DER(1.0)').data
    assert data.shape == (1, 16)


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
    pysdmx.io.xml.sdmx21.reader.data_read.READING_CHUNKSIZE = 100
    data_path = samples_folder / filename
    result = read(data_path, validate=True)
    assert result is not None
    assert any(ds.short_urn == 'DataStructure=BIS:BIS_DER(1.0)' for ds in result)
    data = next(ds for ds in result if ds.short_urn == 'DataStructure=BIS:BIS_DER(1.0)').data
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
    content = read(data_path, validate=True)
    assert content is not None
    assert any(ds.short_urn == 'DataStructure=BIS:BIS_DER(1.0)' for ds in content)
    shape_read = next(ds for ds in content if ds.short_urn == 'DataStructure=BIS:BIS_DER(1.0)').data.shape
    assert shape_read == (1000, 20)
    result = write_xml(content, MessageType.StructureSpecificDataSet)
    content_result = read(result, validate=True)
    # Check we read the same data
    assert content_result is not None
    assert any(ds.short_urn == 'DataStructure=BIS:BIS_DER(1.0)' for ds in content_result)
    data_written = next(ds for ds in content_result if ds.short_urn == 'DataStructure=BIS:BIS_DER(1.0)').data
    shape_written = data_written.shape
    assert shape_read == shape_written


def test_vtl_transformation_scheme(samples_folder):
    data_path = samples_folder / "transformation_scheme.xml"
    result = read(data_path, validate=True)
    assert any(isinstance(ts, TransformationScheme) for ts in result)
    assert len(result) == 1
    urn = 'urn:sdmx:org.sdmx.infomodel.transformation.TransformationScheme=SDMX:TEST(1.0)'
    transformation_scheme = next(ts for ts in result if ts.urn == urn)
    assert transformation_scheme.id == "TEST"
    assert transformation_scheme.name == "TEST"
    assert transformation_scheme.description == "TEST Transformation Scheme"
    assert transformation_scheme.valid_from == datetime(2024, 12, 3, 0, 0)

    assert len(transformation_scheme.items) == 1
    transformation = transformation_scheme.items[0]
    assert isinstance(transformation, Transformation)
    assert transformation.id == "test_rule"
    assert transformation.full_expression == "DS_r <- DS_1 + 1;"
