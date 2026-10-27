"""SDMX XML 2.1 StructureSpecificData reader module."""

from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__ss_aux_reader import read_structure_specific
from pysdmx.io.xml.__tokens import (
    STR_SPE,
    STR_SPE_TS,
)


def read_stream(
    chunks: Iterable[str], validate: bool = True
) -> Tuple[Optional[Dict[str, Any]], List[PandasDataset]]:
    """Reads an SDMX-ML 2.1 StructureSpecific data message in chunks.

    The message is read in a single pass, which also validates it.

    Args:
        chunks: The text of the message, in chunks.
        validate: If True, the XML data will be validated against the XSD.

    Returns:
        The Header of the message, as xmltodict parses it, and the
        datasets.

    Raises:
        Invalid: If the message is not valid SDMX-ML StructureSpecific
            data.
    """
    return read_structure_specific(chunks, validate, (STR_SPE, STR_SPE_TS))


def read(input_str: str, validate: bool = True) -> Sequence[PandasDataset]:
    """Reads an SDMX-ML 2.1 and returns a Sequence of Datasets.

    The message is read in a single pass, which also validates it.

    Args:
        input_str: SDMX-ML data to read.
        validate: If True, the XML data will be validated against the XSD.
    """
    return read_stream([input_str], validate)[1]
