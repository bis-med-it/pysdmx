"""XML readers and writers."""

from pathlib import Path
from typing import Dict, Optional, Sequence, Union

from pysdmx.errors import Invalid
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.reader import read_xml
from pysdmx.io.xml.sdmx21.writer import writer
from pysdmx.model import Codelist, ConceptScheme
from pysdmx.model.dataflow import Dataflow, DataStructureDefinition
from pysdmx.model.message import Header

STR_TYPES = Union[Codelist, ConceptScheme, DataStructureDefinition, Dataflow]
STR_DICT_TYPE = Dict[str, STR_TYPES]
ALL_TYPES = Union[STR_DICT_TYPE, PandasDataset]


def read(
    infile: Union[str, Path],
    validate: bool = False,
    use_dataset_id: bool = False,
) -> Dict[str, ALL_TYPES]:
    """Reads an SDMX-ML file and returns a dictionary with the parsed data."""
    if isinstance(infile, Path):
        infile = str(infile)

    input_str, filetype = process_string_to_read(infile)

    if filetype == "xml":
        return read_xml(
            input_str,
            validate=validate,
            mode=None,
            use_dataset_id=use_dataset_id,
        )
    else:
        raise Invalid(
            "Invalid file type", f"File type {filetype} is not supported."
        )


def _write_common(
    datasets: Union[Dict[str, any], Sequence[Dict[str, any]]],
    output_path: Optional[str],
    prettyprint: bool,
    header: Optional[Header],
    dimension_at_observation: Optional[Dict[str, str]],
    type_: MessageType,
) -> Optional[Union[str, Sequence[str]]]:
    """Internal common logic for writing data or metadata."""
    result: Union[str, Sequence[str]] = (
        [] if isinstance(datasets, Sequence) else None
    )

    if output_path is None:
        output_path = ""

    if not isinstance(datasets, Sequence):
        datasets = [datasets]

    for content in datasets:
        if header is None:
            header = Header()

        xml_str = writer(
            content,
            type_=type_,
            path=output_path,
            prettyprint=prettyprint,
            header=header,
            dimension_at_observation=dimension_at_observation,
        )
        if isinstance(result, list):
            result.append(xml_str)
        else:
            result = xml_str

    return result


def write_data(
    datasets: Union[
        Dict[str, PandasDataset], Sequence[Dict[str, PandasDataset]]
    ],
    output_path: Optional[str] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
    dimension_at_observation: Optional[Dict[str, str]] = None,
) -> Optional[Union[str, Sequence[str]]]:
    """Converts a list of datasets to an SDMX-ML format (data)."""
    return _write_common(
        datasets=datasets,
        output_path=output_path,
        prettyprint=prettyprint,
        header=header,
        dimension_at_observation=dimension_at_observation,
        type_=MessageType.StructureSpecificDataSet,
    )


def write_metadata(
    datasets: Union[
        Dict[str, STR_DICT_TYPE], Sequence[Dict[str, STR_DICT_TYPE]]
    ],
    output_path: Optional[str] = None,
    prettyprint: bool = True,
    header: Optional[Header] = None,
    dimension_at_observation: Optional[Dict[str, str]] = None,
) -> Optional[Union[str, Sequence[str]]]:
    """Converts a list of datasets to an SDMX-ML format (metadata)."""
    return _write_common(
        datasets=datasets,
        output_path=output_path,
        prettyprint=prettyprint,
        header=header,
        dimension_at_observation=dimension_at_observation,
        type_=MessageType.Structure,
    )
