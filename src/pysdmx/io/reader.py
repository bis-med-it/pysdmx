"""SDMX All formats reader module."""

from io import BytesIO
from pathlib import Path
from typing import Dict, Optional, Sequence, Union

from pysdmx.errors import Invalid
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.model import Schema
from pysdmx.model.__base import ItemScheme
from pysdmx.model.dataflow import Dataflow, DataStructureDefinition
from pysdmx.model.dataset import Dataset
from pysdmx.model.message import Message
from pysdmx.model.submission import SubmissionResult
from pysdmx.util import parse_short_urn
from pysdmx.util._model_utils import schema_generator


def read_sdmx(  # noqa: C901
    sdmx_document: Union[str, Path, BytesIO],
    validate: bool = True,
) -> Message:
    """Reads any SDMX message and extracts its content.

    Check the :ref:`formats supported <io-reader-formats-supported>`

    Args:
        sdmx_document: Path to file
          (`pathlib.Path <https://docs.python.org/3/library/pathlib.html>`_),
          URL, or string.
        validate: Validate the input file (only for SDMX-ML).

    Raises:
        Invalid: If the file is empty or the format is not supported.
    """
    input_str, read_format = process_string_to_read(sdmx_document)

    header = None
    result_data: Sequence[Dataset] = []
    result_structures: Sequence[
        Union[ItemScheme, Dataflow, DataStructureDefinition]
    ] = []
    result_submission: Sequence[SubmissionResult] = []
    if read_format == Format.STRUCTURE_SDMX_ML_2_1:
        from pysdmx.io.xml.header import read as read_header
        from pysdmx.io.xml.sdmx21.reader.structure import (
            read as read_structure,
        )

        header = read_header(input_str, validate=validate)
        # SDMX-ML 2.1 Structure
        result_structures = read_structure(input_str, validate=validate)
    elif read_format == Format.STRUCTURE_SDMX_ML_3_0:
        from pysdmx.io.xml.header import read as read_header
        from pysdmx.io.xml.sdmx30.reader.structure import (
            read as read_structure,
        )

        header = read_header(input_str, validate=validate)
        # SDMX-ML 3.0 Structure
        result_structures = read_structure(input_str, validate=validate)
    elif read_format == Format.DATA_SDMX_ML_2_1_GEN:
        from pysdmx.io.xml.header import read as read_header
        from pysdmx.io.xml.sdmx21.reader.generic import read as read_generic

        header = read_header(input_str, validate=validate)
        # SDMX-ML 2.1 Generic Data
        result_data = read_generic(input_str, validate=validate)
    elif read_format == Format.DATA_SDMX_ML_2_1_STR:
        from pysdmx.io.xml.header import read as read_header
        from pysdmx.io.xml.sdmx21.reader.structure_specific import (
            read as read_str_spe,
        )

        header = read_header(input_str, validate=validate)

        # SDMX-ML 2.1 Structure Specific Data
        result_data = read_str_spe(input_str, validate=validate)
    elif read_format == Format.REGISTRY_SDMX_ML_2_1:
        from pysdmx.io.xml.sdmx21.reader.submission import read as read_sub

        # SDMX-ML 2.1 Submission
        result_submission = read_sub(input_str, validate=validate)
    elif read_format == Format.ERROR_SDMX_ML_2_1:
        from pysdmx.io.xml.sdmx21.reader.error import read as read_error

        # SDMX-ML 2.1 Error
        read_error(input_str, validate=validate)
    elif read_format == Format.DATA_SDMX_ML_3_0:
        from pysdmx.io.xml.header import read as read_header
        from pysdmx.io.xml.sdmx30.reader.structure_specific import (
            read as read_str_spe,
        )

        header = read_header(input_str, validate=validate)

        # SDMX-ML 3.0 Structure Specific Data
        result_data = read_str_spe(input_str, validate=validate)
    elif read_format == Format.DATA_SDMX_CSV_1_0_0:
        from pysdmx.io.csv.sdmx10.reader import read as read_csv_v1

        # SDMX-CSV 1.0
        result_data = read_csv_v1(input_str)
    else:
        # SDMX-CSV 2.0
        from pysdmx.io.csv.sdmx20.reader import read as read_csv_v2

        result_data = read_csv_v2(input_str)

    if not (result_data or result_structures or result_submission):
        raise Invalid("Empty SDMX Message")

    # Returning a Message class
    if read_format in (
        Format.DATA_SDMX_CSV_1_0_0,
        Format.DATA_SDMX_CSV_2_0_0,
        Format.DATA_SDMX_ML_2_1_GEN,
        Format.DATA_SDMX_ML_2_1_STR,
        Format.DATA_SDMX_ML_3_0,
    ):
        # TODO: Add here the Schema download for Datasets, based on structure
        # TODO: Ensure we have changed the signature of the data readers
        return Message(header=header, data=result_data)
    elif read_format == Format.REGISTRY_SDMX_ML_2_1:
        return Message(header=header, submission=result_submission)

    # TODO: Ensure we have changed the signature of the structure readers
    return Message(header=header, structures=result_structures)


def __manage_dataset_level_attributes(dataset: Dataset) -> None:
    """Manage attributes at dataset level and remove them from data."""
    # This function requires the dataset to have a structure defined.
    dataset_level_attributes = [
        x
        for x in dataset.structure.components.attributes  # type: ignore[union-attr]
        if x.attachment_level == "D"
    ]
    if len(dataset.attributes) > 0:
        # If the dataset already has attributes, we do not need to add them
        return
    attached_attributes: Dict[str, Optional[str]] = {}
    for att in dataset_level_attributes:
        if att.id not in dataset.data.columns:  # type: ignore[attr-defined]
            attached_attributes[att.id] = None
        else:
            attached_attributes[att.id] = (
                dataset.data[att.id].unique().tolist()[0]  # type: ignore[attr-defined]
            )
            del dataset.data[att.id]  # type: ignore[attr-defined]
    dataset.attributes = attached_attributes


def __assign_structure_to_dataset(
    datasets: Sequence[Dataset], structure_msg: Message
) -> None:
    for dataset in datasets:
        short_urn: str = (
            dataset.structure.short_urn
            if isinstance(dataset.structure, Schema)
            else dataset.structure
        )
        dataset_ref = parse_short_urn(short_urn)
        dataset.structure = schema_generator(structure_msg, dataset_ref)
        __manage_dataset_level_attributes(dataset)


def get_datasets(
    data: Union[str, Path, BytesIO],
    structure: Optional[Union[str, Path, BytesIO]] = None,
    validate: bool = True,
) -> Sequence[Dataset]:
    """Reads a data message and a structure message and returns a dataset.

    This method reads a data message and an optional structure message,
    and returns a sequence of Datasets.
    Check the :ref:`formats supported <io-reader-formats-supported>`

    The resulting datasets will have their structure assigned,
    this is required for:

    - Data validation against its structure
    - Data writing in SDMX-ML Structure Specific with DimensionAtObservation
      not equal to AllDimensions or Generic formats
    - Execution of VTL scripts over PandasDataset

    Args:
        data: Path to file
          (`pathlib.Path <https://docs.python.org/3/library/pathlib.html>`_),
          URL, or string for the data message.
        structure:
          Path to file
          (`pathlib.Path <https://docs.python.org/3/library/pathlib.html>`_),
          URL, or string for the structure message, if needed.
        validate: Validate the input file (only for SDMX-ML).

    Raises:
        Invalid:
            If the data message is empty or the related data structure
            (or dataflow with its children) is not found.
        NotFound:
            If the related data structure (or dataflow with its children)
            is not found.
    """
    data_msg = read_sdmx(data, validate=validate)
    if not data_msg.data:
        raise Invalid("No data found in the data message")

    if structure is None:
        return data_msg.data
    structure_msg = read_sdmx(structure, validate=validate)
    if structure_msg.structures is None:
        raise Invalid("No structure found in the structure message")

    __assign_structure_to_dataset(data_msg.data, structure_msg)

    return data_msg.data
