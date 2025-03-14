"""SDMX 2.1 XML Header reader module."""

from typing import Any, Dict, Optional

from pysdmx.errors import Invalid
from pysdmx.io.xml.sdmx21.__tokens import (
    DATASET_ACTION,
    DATASET_ID,
    HEADER,
    HEADER_ID,
    PREPARED,
    RECEIVER,
    SENDER,
    SOURCE,
    STRUCTURE,
    TEST,
)
from pysdmx.io.xml.sdmx21.reader.__parse_xml import parse_xml
from pysdmx.model.message import Header


def __parse_header(header: Dict[str, Any]) -> Header:
    """Parses the header of the SDMX message.

    Args:
        header: Dictionary with the header information.

    Returns:
        Header: The header of the SDMX message.

    Raises:
        Invalid: If the header is missing required fields.
    """
    required_fields = [HEADER_ID, TEST, PREPARED, SENDER]
    missing_fields = [
        field for field in required_fields if field not in header
    ]

    if missing_fields:
        raise Invalid(
            f"Missing required fields in header: {', '.join(missing_fields)}"
        )

    parsed_header = Header(
        id=header[HEADER_ID],
        test=header[TEST],
        prepared=header[PREPARED],
        sender=header[SENDER],
        receiver=header.get(RECEIVER),
        source=header.get(SOURCE),
        dataset_action=header.get(DATASET_ACTION),
        structure=header.get(STRUCTURE),
        dataset_id=header.get(DATASET_ID),
    )

    return parsed_header


def read(
    input_str: str,
    validate: bool = True,
) -> Optional[Header]:
    """Reads and retrieves the header of the SDMX message.

    Args:
        input_str: The input string to be parsed.
        validate: If True, the SDMX-ML data will be validated against the XSD.

    Returns:
        The header of the SDMX message.
    """
    dict_info = parse_xml(input_str, validate)
    possible_keys = ["StructureSpecificData", "GenericData", "Structure"]
    selected_key = next(
        (key for key in possible_keys if key in dict_info), None
    )
    if selected_key is None or HEADER not in dict_info[selected_key]:
        return None
    header = dict_info[selected_key][HEADER]
    return __parse_header(header)
