"""SDMX 2.1 writer package."""

from pathlib import Path
from typing import Any, Dict, Optional

from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.writer.__write_aux import (
    __write_header,
    check_content_dataset,
    check_dimension_at_observation,
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
    path: Optional[Path] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
    dimension_at_observation: Optional[Dict[str, str]] = None,
) -> Optional[str]:
    """This function writes a SDMX-ML file from the Message Content.

    Args:
        content: The content to be written
        type_: The type of message to be written
        path: The path to save the file
        prettyprint: Prettyprint or not
        header: The header to be used (generated if None)
        dimension_at_observation:
          The mapping between the dataset and the dimension at observation

    Returns:
        The XML string if path is empty, None otherwise
    """
    if header is None:
        header = Header()

    ss_namespaces = ""
    add_namespace_structure = False

    # Checking if we have datasets,
    # we need to ensure we can write them correctly
    dim_mapping: Dict[str, str] = {}
    if type_ in (
        MessageType.StructureSpecificDataSet,
        MessageType.GenericDataSet,
    ):
        check_content_dataset(content)
        # Checking the dimension at observation mapping
        dim_mapping = check_dimension_at_observation(
            content, dimension_at_observation
        )
        header.structure = dim_mapping
        if type_ == MessageType.StructureSpecificDataSet:
            add_namespace_structure = True
            for i, (short_urn, dimension) in enumerate(
                header.structure.items()
            ):
                ss_namespaces += (
                    f'xmlns:ns{i + 1}="urn:sdmx:org.sdmx'
                    f".infomodel.datastructure.{short_urn}"
                    f':ObsLevelDim:{dimension}" '
                )

    # Generating the initial tag with namespaces
    outfile = create_namespaces(type_, ss_namespaces, prettyprint)
    # Generating the header
    outfile += __write_header(header, prettyprint, add_namespace_structure)
    # Writing the content
    if type_ == MessageType.Structure:
        outfile += write_structures(content, prettyprint)
    if type_ == MessageType.StructureSpecificDataSet:
        outfile += write_data_structure_specific(
            content, dim_mapping, prettyprint
        )
    if type_ == MessageType.GenericDataSet:
        outfile += write_data_generic(content, dim_mapping, prettyprint)

    outfile += get_end_message(type_, prettyprint)

    if path is None:
        return outfile

    with open(path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)

    return None
