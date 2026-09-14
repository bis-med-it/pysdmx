"""Read SDMX-ML submission messages."""

from typing import Any, Dict, Sequence

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.xml.__parse_xml import parse_xml
from pysdmx.io.xml.__tokens import (
    ACTION,
    HEADER,
    MAINTAINABLE_OBJECT,
    REG_INTERFACE,
    STATUS,
    STATUS_MSG,
    SUBMISSION_RESULT,
    SUBMIT_STRUCTURE_RESPONSE,
    SUBMITTED_STRUCTURE,
    URN,
)
from pysdmx.io.xml.utils import add_list
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
    for submission_result in add_list(response[SUBMISSION_RESULT]):
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

    Raises:
        Invalid: If the document is not an SDMX-ML 2.1 RegistryInterface
            message.
        NotImplemented: If the RegistryInterface message contains anything
            other than a SubmitStructureResponse (e.g. a
            SubmitStructureRequest or a QueryRegistrationResponse).
    """
    dict_info = parse_xml(input_str, validate=validate)
    if REG_INTERFACE not in dict_info:
        raise Invalid("This SDMX document is not an SDMX-ML 2.1 Submission.")
    if SUBMIT_STRUCTURE_RESPONSE not in dict_info[REG_INTERFACE]:
        # Keys with a colon (e.g. xsi:schemaLocation) and xmlns are
        # attributes of the root element, not content: element names
        # have their namespace prefixes stripped during parsing.
        content = ", ".join(
            key
            for key in dict_info[REG_INTERFACE]
            if key != HEADER and key != "xmlns" and ":" not in key
        )
        raise NotImplemented(
            "Unsupported RegistryInterface content",
            f"Only SubmitStructureResponse messages are supported. "
            f"Found: {content}.",
        )
    return __handle_registry_interface(dict_info)
