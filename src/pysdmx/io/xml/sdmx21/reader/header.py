"""SDMX 2.1 XML Header reader module."""

import re
from typing import Any, Dict, Optional

from pysdmx.io.xml.sdmx21.__tokens import (
    AGENCY_ID,
    CLASS,
    DATASET_ACTION,
    DATASET_ID,
    DIM_OBS,
    DIMENSIONATOBSERVATION,
    GENERIC,
    HEADER,
    HEADER_ID,
    ID,
    NAME,
    NAMES,
    NAMESPACE,
    PREPARED,
    RECEIVER,
    REF,
    SENDER,
    SOURCE,
    STR_SPE,
    STRUCTURE,
    TEST,
    VERSION,
)
from pysdmx.io.xml.sdmx21.reader.__parse_xml import parse_xml
from pysdmx.model.message import Header


def __parse_sender_receiver(
    sender_receiver: Dict[str, Any],
) -> Dict[str, Any] | None:
    """Parses the sender or receiver of the SDMX message."""
    sender_receiver_dict: Dict[str, Any] = {}
    if sender_receiver is None:
        return None
    else:
        names = sender_receiver.get(NAME)
        if names is not None:
            if not isinstance(names, list):
                names = [names]
            sender_receiver_dict[NAMES] = [f"name={name}" for name in names]
        sender_receiver_dict[ID] = sender_receiver.get(ID)
        return sender_receiver_dict


def __parse_structure(structure: Dict[str, Any]) -> str | None:
    """Parses the structure of the SDMX header."""
    if structure is None:
        return None
    elif structure.get(NAMESPACE) is not None:
        match = re.search(
            r"([^.]+)=([^:]+):([^(]+)\(([^)]+)\)",
            structure.get(NAMESPACE),  # type: ignore[arg-type]
        )
        namespace = (
            f"{match.group(1)}={match.group(2)}:{match.group(3)}({match.group(4)}):"  # type: ignore[union-attr]
            f"{structure.get(DIMENSIONATOBSERVATION)}"
        )
        return namespace
    else:
        reference = structure.get(STRUCTURE).get(REF)  # type: ignore[union-attr]
        return (
            f"{reference.get(CLASS)}={reference.get(AGENCY_ID)}:"
            f"{reference.get(ID)}({reference.get(VERSION)}):"
            f"{structure.get(DIM_OBS)}"
        )


def __parse_header(header: Dict[str, Any]) -> Header:
    """Parses the header of the SDMX message.

    Args:
        header: Dictionary with the header information.

    Returns:
        Header: The header of the SDMX message.

    """
    dict_header = {
        "id": header.get(HEADER_ID),
        "test": header.get(TEST),
        "prepared": header.get(PREPARED),
        "sender": __parse_sender_receiver(header.get(SENDER)),  # type: ignore[arg-type]
        "receiver": __parse_sender_receiver(header.get(RECEIVER)),  # type: ignore[arg-type]
        "source": header.get(SOURCE),
        "dataset_action": header.get(DATASET_ACTION),
        "structure": __parse_structure(header.get(STRUCTURE)),  # type: ignore[arg-type]
        "dataset_id": header.get(DATASET_ID),
    }

    return Header(**dict_header)  # type: ignore[arg-type]


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
