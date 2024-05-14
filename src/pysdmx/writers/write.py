"""Writing SDMX-ML files from Message content."""

from typing import Any, Dict, Optional

from pysdmx.model import Code, Codelist, Concept, ConceptScheme
from pysdmx.model.message import MessageType
from pysdmx.writers.__write_aux import (
    create_namespaces,
    generate_new_header,
    generate_structures,
    get_end_message,
)


def writer(
    content: Dict[str, Any],
    type_: MessageType,
    path: str = "",
    prettyprint: bool = True,
) -> Optional[str]:
    """This function writes a SDMX-ML file from the Message Content.

    Args:
        content: The content to be written
        type_: The type of message to be written
        path: The path to save the file
        prettyprint: Prettyprint or not

    Returns:
        The XML string if path is empty, None otherwise

    """
    outfile = create_namespaces(type_, content, prettyprint)

    outfile += generate_new_header(type_, content, prettyprint)

    if type_ == MessageType.Metadata:
        outfile += generate_structures(content, prettyprint)

    outfile += get_end_message(type_, prettyprint)

    if path == "":
        return outfile

    with open(path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)

    return None
