"""SDMX All formats reader module."""

from io import BytesIO
from pathlib import Path
from typing import Sequence, Union

from pysdmx.errors import Invalid, NotFound
from pysdmx.io.enums import SDMXFormat
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.model import Schema
from pysdmx.model.dataset import Dataset
from pysdmx.model.message import Message
from pysdmx.util import parse_short_urn


def read_sdmx(
    sdmx_document: Union[str, Path, BytesIO],
    validate: bool = True,
) -> Message:
    """Reads any SDMX message and returns a dictionary.

    Supported metadata formats are:
    - SDMX-ML 2.1

    Supported data formats are:
    - SDMX-ML 2.1
    - SDMX-CSV 1.0
    - SDMX-CSV 2.0

    Args:
        sdmx_document: Path to file (pathlib.Path), URL, or string.
        validate: Validate the input file (only for SDMX-ML).

    Returns:
        A dictionary containing the parsed SDMX data or metadata.

    Raises:
        Invalid: If the file is empty or the format is not supported.
    """
    input_str, read_format = process_string_to_read(sdmx_document)

    if read_format == SDMXFormat.SDMX_ML_2_1_STRUCTURE:
        # SDMX-ML 2.1 Structure
        from pysdmx.io.xml.sdmx21.reader.structure import read

        result = read(input_str)
    elif read_format == SDMXFormat.SDMX_ML_2_1_DATA_GENERIC:
        # SDMX-ML 2.1 Generic Data
        from pysdmx.io.xml.sdmx21.reader.generic import read

        result = read(input_str, validate=validate)
    elif read_format == SDMXFormat.SDMX_ML_2_1_DATA_STRUCTURE_SPECIFIC:
        # SDMX-ML 2.1 Structure Specific Data
        from pysdmx.io.xml.sdmx21.reader.structure_specific import read

        result = read(input_str)
    elif read_format == SDMXFormat.SDMX_ML_2_1_SUBMISSION:
        # SDMX-ML 2.1 Submission
        from pysdmx.io.xml.sdmx21.reader.submission import read

        result = read(input_str)
    elif read_format == SDMXFormat.SDMX_ML_2_1_ERROR:
        # SDMX-ML 2.1 Error
        from pysdmx.io.xml.sdmx21.reader.error import read

        result = read(input_str)
    elif read_format == SDMXFormat.SDMX_CSV_1_0:
        # SDMX-CSV 1.0
        from pysdmx.io.csv.sdmx10.reader import read

        result = read(input_str)
    else:
        # SDMX-CSV 2.0
        from pysdmx.io.csv.sdmx20.reader import read

        result = read(input_str)

    if len(result) == 0:
        raise Invalid("Empty SDMX Message")

    # Returning a Message class
    if read_format in (
        SDMXFormat.SDMX_CSV_1_0,
        SDMXFormat.SDMX_CSV_2_0,
        SDMXFormat.SDMX_ML_2_1_DATA_GENERIC,
        SDMXFormat.SDMX_ML_2_1_DATA_STRUCTURE_SPECIFIC,
    ):
        # TODO: Add here the Schema download for Datasets, based on structure
        # TODO: Ensure we have changed the signature of the data readers
        return Message(data=result)
    elif read_format == SDMXFormat.SDMX_ML_2_1_SUBMISSION:
        return Message(submission=result)

    # TODO: Ensure we have changed the signature of the structure readers
    return Message(structures=result)


def get_datasets(
    data: Union[str, Path, BytesIO],
    structure: Union[str, Path, BytesIO],
    validate: bool = True,
) -> Sequence[Dataset]:
    """Reads a data message and a structure message and returns a dataset.

    Args:
        data: Path to file (pathlib.Path), URL, or string for the data message.
        structure:
          Path to file (pathlib.Path), URL, or string
          for the structure message.
        validate: Validate the input file (only for SDMX-ML).

    Returns:
        A sequence of Datasets

    Raises:
        Invalid:
            If the data message is empty or the related data structure
            (or dataflow with its children) is not found.
    """
    data_msg = read_sdmx(data, validate=validate)
    if not data_msg.data:
        raise Invalid("No data found in the data message")

    structure_msg = read_sdmx(structure, validate=validate)
    if structure_msg.structures is None:
        raise Invalid("No structure found in the structure message")

    for dataset in data_msg.data:
        short_urn: str = (
            dataset.structure.short_urn
            if isinstance(dataset.structure, Schema)
            else dataset.structure
        )
        sdmx_type = parse_short_urn(short_urn).sdmx_type
        if sdmx_type == "DataStructure":
            try:
                dsd = structure_msg.get_data_structure_definition(short_urn)
                dataset.structure = dsd.to_schema()
            except NotFound:
                continue
        elif sdmx_type == "DataFlow":
            try:
                dataflow = structure_msg.get_dataflow(short_urn)
                if dataflow.structure is None:
                    continue
                dsd = structure_msg.get_data_structure_definition(
                    dataflow.structure
                )
                dataflow.structure = dsd.to_schema()
            except NotFound:
                continue

    return list(data_msg.data)
