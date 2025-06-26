"""Parsers for reading metadata."""

from typing import Sequence, Union

from pysdmx.errors import Invalid
from pysdmx.io.xml.__parse_xml import parse_xml
from pysdmx.io.xml.__structure_aux_reader import StructureParser
from pysdmx.io.xml.__tokens import (
    STRUCTURE,
    STRUCTURES,
)
from pysdmx.model.__base import (
    ItemScheme,
)
from pysdmx.model.dataflow import (
    Dataflow,
    DataStructureDefinition,
)


def read(
    input_str: str,
    validate: bool = True,
) -> Sequence[Union[ItemScheme, DataStructureDefinition, Dataflow]]:
    """Reads an SDMX-ML 2.1 Structure data and returns the structures.

    Args:
        input_str: SDMX-ML structure message to read.
        validate: If True, the XML data will be validated against the XSD.

    Returns:
        dict: Dictionary with the parsed structures.
    """
    dict_info = parse_xml(input_str, validate)
    if STRUCTURE not in dict_info:
        raise Invalid("This SDMX document is not SDMX-ML 2.1 Structure.")
    return StructureParser().format_structures(
        dict_info[STRUCTURE][STRUCTURES]
    )
