"""Read SDMX-ML submission messages."""

from typing import Any, Dict

from pysdmx.io.xml.sdmx21.__parsing_config import (
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
from pysdmx.model.message import SubmissionResult
from pysdmx.util import parse_urn


def handle_registry_interface(dict_info: Dict[str, Any]) -> Dict[str, Any]:
    """Handle the Registry Interface message.

    Args:
        dict_info: Dictionary with the parsed data.

    Returns:
        dict: Dictionary with the parsed data.
    """
    response = dict_info[REG_INTERFACE][SUBMIT_STRUCTURE_RESPONSE]

    result = {}
    for submission_result in response[SUBMISSION_RESULT]:
        structure = submission_result[SUBMITTED_STRUCTURE]
        action = structure[ACTION]
        urn = structure[MAINTAINABLE_OBJECT][URN]
        short_urn = str(parse_urn(urn))
        status = submission_result[STATUS_MSG][STATUS]
        result[short_urn] = SubmissionResult(action, short_urn, status)
    return result
