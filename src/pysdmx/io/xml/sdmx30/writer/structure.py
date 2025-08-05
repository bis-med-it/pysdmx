"""Module for writing metadata to XML files."""

from pathlib import Path
from typing import Dict, Optional, Sequence, Union

from pysdmx.io.format import Format
from pysdmx.io.xml.__structure_aux_writer import (
    STR_DICT_TYPE_LIST_30,
    __write_structures,
)
from pysdmx.io.xml.__write_aux import (
    __write_header,
    create_namespaces,
    get_end_message,
)
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.message import Header


def write(
    structures: Sequence[MaintainableArtefact],
    output_path: Optional[Union[str, Path]] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> Optional[str]:
    """This function writes a SDMX-ML file from the Message Content.

    Args:
        structures: The content to be written
        output_path: The path to save the file
        prettyprint: Prettyprint or not
        header: The header to be used (generated if None)

    Returns:
        The XML string if output_path is empty, None otherwise
    """
    type_ = Format.STRUCTURE_SDMX_ML_3_0
    elements = {structure.short_urn: structure for structure in structures}
    if header is None:
        header = Header()

    content: Dict[str, Dict[str, MaintainableArtefact]] = {}
    for urn, element in elements.items():
        list_ = STR_DICT_TYPE_LIST_30[type(element)]
        if list_ not in content:
            content[list_] = {}
        content[list_][urn] = element

    # Generating the initial tag with namespaces
    outfile = create_namespaces(type_, prettyprint=prettyprint)
    # Generating the header
    outfile += __write_header(header, prettyprint, data_message=False)
    # Writing the content
    outfile += __write_structures(content, prettyprint, references_30=True)

    outfile += get_end_message(type_, prettyprint)

    output_path = (
        str(output_path) if isinstance(output_path, Path) else output_path
    )

    if output_path is None or output_path == "":
        return outfile

    with open(output_path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)
    return None
