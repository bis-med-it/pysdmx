from pathlib import Path

import pytest

from pysdmx.errors import ClientError
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.reader import read_xml
from pysdmx.model.message import SubmissionResult


# Test parsing SDMX Registry Interface Submission Response


@pytest.fixture()
def submission_path():
    return Path(__file__).parent / "samples" / "submission_append.xml"


@pytest.fixture()
def error_304_path():
    return Path(__file__).parent / "samples" / "error_304.xml"


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
