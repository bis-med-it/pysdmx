"""Read SDMX-ML submission messages."""

from typing import Any, Dict, Sequence

from pysdmx.io.xml.sdmx21.__tokens import (
    ACTION,
    MAINTAINABLE_OBJECT,
    REG_INTERFACE,
    STATUS,
    STATUS_MSG,
    SUBMISSION_RESULT,
    SUBMIT_STRUCTURE_RESPONSE,
    SUBMITTED_STRUCTURE,
    URN,
)
from pysdmx.io.xml.sdmx21.reader.__parse_xml import parse_xml
from pysdmx.model.submission import SubmissionResult
from pysdmx.util import parse_urn


def __handle_registry_interface(
    dict_info: Dict[str, Any],
) -> Sequence[SubmissionResult]:
    """Handle the Registry Interface message.

    Args:
        dict_info: Dictionary with the parsed data.

    Returns:
        dict: Dictionary with the parsed data.
    """
    response = dict_info[REG_INTERFACE][SUBMIT_STRUCTURE_RESPONSE]

    result = []
    for submission_result in response[SUBMISSION_RESULT]:
        structure = submission_result[SUBMITTED_STRUCTURE]
        action = structure[ACTION]
        urn = structure[MAINTAINABLE_OBJECT][URN]
        short_urn = str(parse_urn(urn))
        status = submission_result[STATUS_MSG][STATUS]
        sr = SubmissionResult(action, short_urn, status)
        result.append(sr)
    return result


def read(infile: str, validate: bool = True) -> Sequence[SubmissionResult]:
    """Reads an SDMX-ML 2.1 Submission Result file.

    Args:
        infile: string to read XML data from.
        validate: If True, the XML data will be validated against the XSD.
    """
    dict_info = parse_xml(infile, validate=validate)
    return __handle_registry_interface(dict_info)
