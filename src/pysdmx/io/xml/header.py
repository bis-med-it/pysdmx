"""SDMX 2.1 XML Header reader module."""

import contextlib
import warnings
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple, Union

import xmltodict

from pysdmx.io.xml.__parse_xml import xml_options
from pysdmx.io.xml.__tokens import (
    AGENCY_ID,
    DATASET_ACTION,
    DATASET_ID,
    DFW,
    DIM_OBS,
    DSD,
    HEADER,
    HEADER_ID,
    ID,
    NAME,
    PREPARED,
    PROV_AGREEMENT,
    PROV_AGREMENT,
    RECEIVER,
    REF,
    SENDER,
    SOURCE,
    STR_USAGE,
    STRUCTURE,
    TEST,
    URN,
    VERSION,
)
from pysdmx.io.xml.doc_validation import validate_doc
from pysdmx.io.xml.utils import add_list
from pysdmx.model import Organisation, Reference
from pysdmx.model.dataset import ActionType
from pysdmx.model.message import Header
from pysdmx.util import ensure_tz_aware, parse_maintainable_urn


def __parse_sender_receiver(
    sender_receiver: Union[Dict[str, Any], None],
) -> Union[Organisation, None]:
    """Parses the sender or receiver of the SDMX message."""
    if sender_receiver is None:
        return None
    names = sender_receiver.get(NAME, None)
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
                    if name.get("lang", "en") == "en"
                ),
                names[0].get("#text"),
            )

    expected_keys = {NAME, ID}
    unexpected_keys = set(sender_receiver.keys()) - expected_keys
    unexpected_keys = {x for x in unexpected_keys if "xml" not in x.lower()}
    if unexpected_keys:
        warnings.warn(
            f"The following attributes will be lost: "
            f"{', '.join(unexpected_keys)}",
            UserWarning,
            stacklevel=2,
        )

    id_ = sender_receiver.get(ID, "ZZZ")

    organisation = Organisation(
        id=id_,
        name=selected_name,
    )

    return organisation


def __parse_structure(
    structure: Union[Dict[str, Any], None],
) -> Union[Dict[str, str], None]:
    """Parses the structure/s of the SDMX header."""
    if structure is None:
        return None

    result = {}

    for struct in add_list(structure):
        dim_at_obs = struct.get(DIM_OBS, "AllDimensions")

        if STRUCTURE in struct:
            structure_info = struct[STRUCTURE]
            sdmx_type = DSD
        elif STR_USAGE in struct:
            structure_info = struct[STR_USAGE]
            sdmx_type = DFW
        elif PROV_AGREEMENT in struct:
            structure_info = struct[PROV_AGREEMENT]
            sdmx_type = PROV_AGREEMENT
        else:
            # Provision Agrement is a typo in the SDMX 2.1 schema,
            # and it is later solved in SDMX 3.0
            structure_info = struct[PROV_AGREMENT]
            sdmx_type = PROV_AGREMENT

        if isinstance(structure_info, dict) and REF in structure_info:
            reference = structure_info[REF]
            agency_id = reference[AGENCY_ID]
            structure_id = reference[ID]
            version = reference[VERSION]
            ref_obj = Reference(
                sdmx_type=sdmx_type,
                agency=agency_id,
                id=structure_id,
                version=version,
            )
        elif URN in structure_info:
            ref_obj = parse_maintainable_urn(structure_info[URN])
        else:
            ref_obj = parse_maintainable_urn(structure_info)

        result[str(ref_obj)] = dim_at_obs

    return result


def __parse_source(source: Optional[Dict[str, Any]]) -> Optional[str]:
    """Parses the source of the SDMX message."""
    if source is None:
        return None
    elif isinstance(source, dict):
        return source["#text"]
    else:
        return source


def __parse_dataset_action(
    dataset_action: Optional[Dict[str, Any]],
) -> Optional[ActionType]:
    """Parses the dataset action of the SDMX message."""
    if dataset_action is None:
        return None
    else:
        return ActionType(dataset_action)


def __parse_prepared(prepared: str) -> datetime:
    """Parses the prepared date of the SDMX message.

    A datetime without timezone information is assumed to be in UTC.
    """
    return ensure_tz_aware(
        datetime.fromisoformat(prepared.replace("Z", "+00:00"))
    )


def __parse_header(header: Dict[str, Any]) -> Header:
    """Parses the header of the SDMX message.

    Args:
        header: Dictionary with the header information.

    Returns:
        Header: The header of the SDMX message.

    """
    if isinstance(header.get(RECEIVER), list):
        receiver = [
            __parse_sender_receiver(r) for r in header.get(RECEIVER, [])
        ]
    else:
        receiver = __parse_sender_receiver(header.get(RECEIVER))  # type: ignore[assignment]
    dict_header = {
        "id": header.get(HEADER_ID),
        "test": header.get(TEST),
        "prepared": __parse_prepared(header.get(PREPARED)),  # type: ignore[arg-type]
        "sender": __parse_sender_receiver(header.get(SENDER)),
        "receiver": receiver,
        "source": __parse_source(header.get(SOURCE)),
        "dataset_action": __parse_dataset_action(header.get(DATASET_ACTION)),
        "structure": __parse_structure(header.get(STRUCTURE)),
        "dataset_id": header.get(DATASET_ID),
    }

    return Header(**dict_header)  # type: ignore[arg-type]


def __read_header_element(input_str: str) -> Optional[Dict[str, Any]]:
    """Parses the message Header, without parsing the rest of the message.

    The Header is always the first child of the message root, so parsing
    stops after that child.

    Args:
        input_str: The SDMX-ML message.

    Returns:
        The parsed Header, or None if the first child of the root is not a
        Header or has no content.
    """
    header: List[Dict[str, Any]] = []

    def first_child(path: List[Tuple[str, Any]], item: Any) -> bool:
        if path[-1][0] == HEADER and isinstance(item, dict):
            header.append(item)
        return False  # Stops parsing after the first child of the root

    with contextlib.suppress(xmltodict.ParsingInterrupted):
        xmltodict.parse(
            input_str,
            item_depth=2,
            item_callback=first_child,
            **xml_options(input_str),
        )
    return header[0] if header else None


def parse_header(header: Optional[Dict[str, Any]]) -> Optional[Header]:
    """Parses the Header of an SDMX-ML message.

    Args:
        header: The Header, as xmltodict parses it, or None.

    Returns:
        The header of the SDMX message, or None if there is no Header.
    """
    if header is None:
        return None
    return __parse_header(header)


def read(
    input_str: str,
    validate: bool = True,
) -> Optional[Header]:
    """Reads and retrieves the header of the SDMX message.

    Only the Header is parsed, not the rest of the message.

    Args:
        input_str: The input string to be parsed.
        validate: If True, the whole SDMX-ML message will be validated
            against the XSD.

    Returns:
        The header of the SDMX message, or None if it has none.
    """
    if validate:
        validate_doc(input_str)
    return parse_header(__read_header_element(input_str))
