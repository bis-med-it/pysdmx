"""SDMX 2.1 XML Header reader module."""

from typing import Any, Dict, Optional

from pysdmx.io.xml.sdmx21.__tokens import (
    DATASET_ACTION,
    DATASET_ID,
    GENERIC,
    HEADER,
    HEADER_ID,
    PREPARED,
    RECEIVER,
    SENDER,
    SOURCE,
    STR_SPE,
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

    """
    dict_header = {
        "id": header[HEADER_ID],
        "test": header[TEST],
        "prepared": header[PREPARED],
        "sender": header[SENDER]["id"]
        if isinstance(header[SENDER], dict)
        else header[SENDER],
        **({"receiver": header[RECEIVER]} if RECEIVER in header else {}),
        **({"source": header[SOURCE]} if SOURCE in header else {}),
        **(
            {"dataset_action": header[DATASET_ACTION]}
            if DATASET_ACTION in header
            else {}
        ),
        **({"structure": header[STRUCTURE]} if STRUCTURE in header else {}),
        **({"dataset_id": header[DATASET_ID]} if DATASET_ID in header else {}),
    }

    return Header(**dict_header)


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
    possible_keys = [STR_SPE, GENERIC, STRUCTURE]
    selected_key = next((key for key in possible_keys if key in dict_info))
    if HEADER not in dict_info[selected_key]:
        return None
    header = dict_info[selected_key][HEADER]
    return __parse_header(header)
