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
    infile: Union[str, Path, BytesIO],
    validate: bool = True,
    use_dataset_id: bool = False,
) -> Message:
    """Reads any sdmx file or buffer and returns a dictionary.

    Supported metadata formats are:
    - SDMX-ML 2.1

    Supported data formats are:
    - SDMX-ML 2.1
    - SDMX-CSV 1.0
    - SDMX-CSV 2.0

    Args:
        infile: Path to file (pathlib.Path), URL, or string.
        use_dataset_id: Whether to use the dataset ID as
            the key in the resulting dictionary (only for SDMX-ML).
        validate: Validate the input file (only for SDMX-ML).

    Returns:
        A dictionary containing the parsed SDMX data or metadata.

    Raises:
        Invalid: If the file is empty or the format is not supported.
    """
    input_str, read_format = process_string_to_read(infile)

    if read_format in (
        SDMXFormat.SDMX_ML_2_1_DATA_GENERIC,
        SDMXFormat.SDMX_ML_2_1_DATA_STRUCTURE_SPECIFIC,
        SDMXFormat.SDMX_ML_2_1_STRUCTURE,
        SDMXFormat.SDMX_ML_2_1_SUBMISSION,
        SDMXFormat.SDMX_ML_2_1_ERROR,
    ):
        # SDMX-ML 2.1
        from pysdmx.io.xml.sdmx21.reader import read_xml

        result = read_xml(
            input_str, validate=validate, use_dataset_id=use_dataset_id
        )
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
    """
    data_msg = read_sdmx(data, validate=validate)
    if not data_msg.data:
        raise Invalid("No data found in the data message")

    structure_msg = read_sdmx(structure, validate=validate)
    if structure_msg.structures is None:
        raise Invalid("No structure found in the structure message")

    for dataset in data_msg.data.values():
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

    return list(data_msg.data.values())
