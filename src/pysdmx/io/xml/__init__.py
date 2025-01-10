"""XML readers and writers."""
from pathlib import Path
from typing import Union, Dict, Sequence

from pysdmx.errors import Invalid
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx21.reader import read_xml
from pysdmx.model import ConceptScheme, Codelist
from pysdmx.model.__base import ItemScheme
from pysdmx.model.dataflow import DataStructureDefinition, Dataflow
from pysdmx.model.message import SubmissionResult

STR_TYPES = Union[ItemScheme, Codelist, ConceptScheme, DataStructureDefinition, Dataflow]
STR_DICT_TYPE = Dict[str, STR_TYPES]
ALL_TYPES = Union[STR_DICT_TYPE, PandasDataset]


def read(
    infile: Union[str, Path],
    validate: bool = False,
    use_dataset_id: bool = False,
) -> Sequence[ALL_TYPES]:
    """Reads an SDMX-ML file and returns a dictionary with the parsed data."""
    input_str, filetype = process_string_to_read(infile)

    if filetype == "xml":
        dict_ = read_xml(
            input_str,
            validate=validate,
            mode=None,
            use_dataset_id=use_dataset_id,
        )
        result = []
        for key, value in dict_.items():
            if isinstance(value, (PandasDataset, SubmissionResult)):
                result.append(value)
            else:
                for item in value.values():
                    result.append(item)
        return result
    else:
        raise Invalid(
            "Invalid file type", f"File type {filetype} is not supported."
        )