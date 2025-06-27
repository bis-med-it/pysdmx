"""Read SDMX-ML submission messages."""

from typing import Any, Dict, Sequence

from pysdmx.errors import Invalid
from pysdmx.io.xml.__parse_xml import parse_xml
from pysdmx.io.xml.__tokens import (
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


def read(input_str: str, validate: bool = True) -> Sequence[SubmissionResult]:
    """Reads an SDMX-ML 2.1 Submission Result file.

    Args:
        input_str: SDMX-ML data to read.
        validate: If True, the XML data will be validated against the XSD.
    """
    dict_info = parse_xml(input_str, validate=validate)
    if REG_INTERFACE not in dict_info:
        raise Invalid("This SDMX document is not an SDMX-ML 2.1 Submission.")
    return __handle_registry_interface(dict_info)
