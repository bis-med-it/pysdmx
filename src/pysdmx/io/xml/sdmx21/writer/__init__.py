"""SDMX 2.1 writer package."""

from typing import Any, Dict, Optional

from pysdmx.errors import NotImplemented
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.writer.__write_aux import (
    __write_header,
    create_namespaces,
    get_end_message,
)
from pysdmx.io.xml.sdmx21.writer.structure import (
    generate_structures,
)
from pysdmx.model.message import Header


def writer(
    content: Dict[str, Any],
    type_: MessageType,
    path: str = "",
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> Optional[str]:
    """This function writes a SDMX-ML file from the Message Content.

    Args:
        content: The content to be written
        type_: The type of message to be written
        path: The path to save the file
        prettyprint: Prettyprint or not
        header: The header to be used (generated if None)

    Returns:
        The XML string if path is empty, None otherwise

    Raises:
        NotImplemented: If the MessageType is not Metadata
    """
    if type_ != MessageType.Structure:
        raise NotImplemented(
            "Unsupported", "Only Metadata messages are supported"
        )
    outfile = create_namespaces(type_, content, prettyprint)

    if header is None:
        header = Header()

    outfile += __write_header(header, prettyprint)

    outfile += generate_structures(content, prettyprint)

    outfile += get_end_message(type_, prettyprint)

    if path == "":
        return outfile

    with open(path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)

    return None
