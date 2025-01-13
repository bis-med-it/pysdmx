"""XML readers and writers."""

from pathlib import Path
from typing import Sequence, Union

from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx21.reader import read_xml
from pysdmx.model import Codelist, ConceptScheme
from pysdmx.model.__base import ItemScheme
from pysdmx.model.dataflow import Dataflow, DataStructureDefinition
from pysdmx.model.message import SubmissionResult

STR_TYPES = Union[
    ItemScheme, Codelist, ConceptScheme, DataStructureDefinition, Dataflow
]
ALL_TYPES = Union[STR_TYPES, PandasDataset, SubmissionResult]


def read(
    infile: Union[str, Path],
    validate: bool = False,
    use_dataset_id: bool = False,
) -> Sequence[ALL_TYPES]:
    """Reads an SDMX-ML file and returns a dictionary with the parsed data."""
    input_str, filetype = process_string_to_read(infile)

    dict_ = read_xml(
        input_str,
        validate=validate,
        use_dataset_id=use_dataset_id,
    )
    result = []
    for _, value in dict_.items():
        if isinstance(value, (PandasDataset, SubmissionResult)):
            result.append(value)
        else:
            for item in value.values():
                result.append(item)
    return result
