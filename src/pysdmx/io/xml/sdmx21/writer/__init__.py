"""SDMX 2.1 writer package."""

from typing import Any, Dict, Optional

from pysdmx.errors import NotImplemented
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.writer.__write_aux import (
    __write_header,
    ALL_DIM,
    check_content_dataset,
    create_namespaces,
    get_end_message,
)
from pysdmx.io.xml.sdmx21.writer.generic import write_data_generic
from pysdmx.io.xml.sdmx21.writer.structure import (
    write_structures,
)
from pysdmx.io.xml.sdmx21.writer.structure_specific import (
    write_data_structure_specific,
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
    if header is None:
        header = Header()

    ss_namespaces = ""
    add_namespace_structure = False

    if type_ in (
        MessageType.StructureSpecificDataSet,
        MessageType.GenericDataSet,
    ):
        check_content_dataset(content)
        header.dataset_references = {k: ALL_DIM for k in content.keys()}
        # TODO: How to set the dimension at observation?
        if type_ == MessageType.StructureSpecificDataSet:
            add_namespace_structure = True
            for i, (short_urn, dimension) in enumerate(
                header.dataset_references.items()
            ):
                ss_namespaces += (
                    f'xmlns:ns{i + 1}="urn:sdmx:org.sdmx'
                    f".infomodel.datastructure.{short_urn}"
                    f':ObsLevelDim:{dimension}" '
                )

    outfile = create_namespaces(type_, ss_namespaces, prettyprint)
    outfile += __write_header(header, prettyprint, add_namespace_structure)
    if type_ == MessageType.Structure:
        outfile += write_structures(content, prettyprint)
    elif type_ == MessageType.StructureSpecificDataSet:
        outfile += write_data_structure_specific(content, prettyprint)
    elif type_ == MessageType.GenericDataSet:
        outfile += write_data_generic(content, prettyprint)
    else:
        raise NotImplemented(f"MessageType {type_} not implemented")

    outfile += get_end_message(type_, prettyprint)

    if path == "":
        return outfile

    with open(path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)

    return None
