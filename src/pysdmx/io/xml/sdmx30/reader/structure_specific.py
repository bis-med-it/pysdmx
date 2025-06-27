"""SDMX XML 3.0 StructureSpecificData reader module."""

from typing import Sequence

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__data_aux import (
    get_data_objects,
)
from pysdmx.io.xml.__parse_xml import parse_xml
from pysdmx.io.xml.__ss_aux_reader import (
    _parse_structure_specific_data,
)
from pysdmx.io.xml.__tokens import (
    STR_REF,
    STR_SPE,
)


def read(input_str: str, validate: bool = True) -> Sequence[PandasDataset]:
    """Reads an SDMX-ML 3.0 and returns a Sequence of Datasets.

    Args:
        input_str: SDMX-ML data to read.
        validate: If True, the XML data will be validated against the XSD.
    """
    dict_info = parse_xml(input_str, validate=validate)
    if STR_SPE not in dict_info:
        raise Invalid(
            "This SDMX document is not an SDMX-ML StructureSpecificData."
        )
    dataset_info, str_info = get_data_objects(dict_info[STR_SPE])
    datasets = []
    for dataset in dataset_info:
        ds = _parse_structure_specific_data(
            dataset, str_info[dataset[STR_REF]]
        )
        datasets.append(ds)
    return datasets
