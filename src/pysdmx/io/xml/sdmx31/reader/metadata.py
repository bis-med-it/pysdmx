"""Reader for SDMX-ML 3.1 reference metadata (GenericMetadata)."""

from typing import Sequence

from pysdmx.io.xml.__metadata_aux_reader import read_metadata
from pysdmx.model.metadata import MetadataReport


def read(
    input_str: str,
    validate: bool = True,
) -> Sequence[MetadataReport]:
    """Reads an SDMX-ML 3.1 GenericMetadata message.

    Args:
        input_str: SDMX-ML GenericMetadata message to read.
        validate: If True, the XML data will be validated against the XSD.

    Returns:
        The sequence of reference metadata reports.
    """
    return read_metadata(input_str, validate)
