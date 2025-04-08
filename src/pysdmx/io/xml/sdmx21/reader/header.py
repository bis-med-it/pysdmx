"""SDMX 2.1 XML Header reader module."""

import re
import warnings
from typing import Any, Dict, Optional, Union

from pysdmx.io.xml.sdmx21.__tokens import (
    AGENCY_ID,
    CLASS,
    DATASET_ACTION,
    DATASET_ID,
    DIM_OBS,
    GENERIC,
    HEADER,
    HEADER_ID,
    ID,
    NAME,
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
from pysdmx.model import Organisation
from pysdmx.model.message import Header


def __parse_sender_receiver(
    sender_receiver: Union[Dict[str, Any], None],
) -> Union[Organisation, None]:
    """Parses the sender or receiver of the SDMX message."""
    if sender_receiver is None:
        return None
    else:
        names = sender_receiver.get(NAME)
        selected_name = None

        if names is not None:
            if not isinstance(names, list):
                names = [names]

            if isinstance(names[0], str):
                selected_name = names[0]

            else:
                selected_name = next(
                    (
                        name.get("#text")
                        for name in names
                        if name.get("lang") == "en"
                    ),
                    names[0].get("#text"),
                )

        expected_keys = {NAME, ID}
        unexpected_keys = set(sender_receiver.keys()) - expected_keys
        if unexpected_keys:
            warnings.warn(
                f"The following attributes will be lost: "
                f"{', '.join(unexpected_keys)}",
                UserWarning,
                stacklevel=2,
            )

        organisation = Organisation(
            id=sender_receiver.get(ID),  # type: ignore[arg-type]
            name=selected_name,
        )

        return organisation


def __parse_structure(
    structure: Union[Dict[str, Any], None],
) -> Union[Dict[str, str], None]:
    """Parses the structure of the SDMX header."""
    structure_dict: Dict[str, str]
    if structure is None:
        return None
    elif structure.get(NAMESPACE) is not None:
        match = re.search(
            r"([^.]+)=([^:]+):([^(]+)\(([^)]+)\)",
            structure.get(NAMESPACE),  # type: ignore[arg-type]
        )
        structure_dict = {
            f"{match.group(1)}={match.group(2)}:"  # type: ignore[dict-item,union-attr]
            f"{match.group(3)}({match.group(4)})": structure.get(DIM_OBS)  # type: ignore[union-attr]
        }
    else:
        reference = structure.get(STRUCTURE).get(REF)  # type: ignore[union-attr]
        structure_dict = {
            f"{reference.get(CLASS)}={reference.get(AGENCY_ID)}:"  # type: ignore[dict-item]
            f"{reference.get(ID)}({reference.get(VERSION)})": structure.get(
                DIM_OBS
            )
        }

    return structure_dict


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
        "sender": __parse_sender_receiver(header.get(SENDER)),
        "receiver": __parse_sender_receiver(header.get(RECEIVER)),
        "source": header.get(SOURCE),
        "dataset_action": header.get(DATASET_ACTION),
        "structure": __parse_structure(header.get(STRUCTURE)),
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
