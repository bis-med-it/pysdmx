"""SDMX 2.1 XML reader package."""

from typing import Any, Dict, Optional

import xmltodict

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.__parsing_config import (
    DATASET,
    ERROR,
    ERROR_CODE,
    ERROR_MESSAGE,
    ERROR_TEXT,
    GENERIC,
    HEADER,
    REG_INTERFACE,
    STRSPE,
    STRUCTURE,
    STRUCTURES,
    XML_OPTIONS,
)
from pysdmx.io.xml.sdmx21.doc_validation import validate_doc
from pysdmx.io.xml.sdmx21.reader.data_read import (
    __extract_structure,
    create_dataset,
)
from pysdmx.io.xml.sdmx21.reader.metadata_read import StructureParser
from pysdmx.io.xml.sdmx21.reader.submission_reader import (
    handle_registry_interface,
)
from pysdmx.io.xml.utils import add_list

MODES = {
    MessageType.GenericDataSet.value: GENERIC,
    MessageType.StructureSpecificDataSet.value: STRSPE,
    MessageType.Structure.value: STRUCTURE,
    MessageType.Submission.value: REG_INTERFACE,
    MessageType.Error.value: ERROR,
}


def read_xml(
    infile: str,
    validate: bool = True,
    mode: Optional[MessageType] = None,
    use_dataset_id: bool = False,
) -> Dict[str, Any]:
    """Reads an SDMX-ML file and returns a dictionary with the parsed data.

    Args:
        infile: Path to file, URL, or string.
        validate: If True, the XML data will be validated against the XSD.
        mode: The type of message to parse.
        use_dataset_id: If True, the dataset ID will be used as the key in the
            resulting dictionary.

    Returns:
        dict: Dictionary with the parsed data.

    Raises:
        Invalid: If the SDMX data cannot be parsed.
    """
    if validate:
        validate_doc(infile)
    dict_info = xmltodict.parse(
        infile, **XML_OPTIONS  # type: ignore[arg-type]
    )

    del infile

    if mode is not None and MODES[mode.value] not in dict_info:
        raise Invalid(
            "Validation Error",
            f"Unable to parse sdmx file as {MODES[mode.value]} file",
        )

    result = __generate_sdmx_objects_from_xml(dict_info, use_dataset_id)

    return result


def __generate_sdmx_objects_from_xml(
    dict_info: Dict[str, Any], use_dataset_id: bool = False
) -> Dict[str, Any]:
    """Generates SDMX objects from the XML dictionary (xmltodict).

    Args:
        dict_info: XML dictionary (xmltodict)
        use_dataset_id: Use the dataset ID as the key in
            the resulting dictionary

    Returns:
        dict: Dictionary with the parsed data.

    Raises:
        Invalid: If a SOAP error message is found.
        NotImplemented: If the SDMX data cannot be parsed.
    """
    if ERROR in dict_info:
        code = dict_info[ERROR][ERROR_MESSAGE][ERROR_CODE]
        text = dict_info[ERROR][ERROR_MESSAGE][ERROR_TEXT]
        raise Invalid("Invalid", f"{code}: {text}")
    if STRSPE in dict_info:
        return __parse_dataset(dict_info[STRSPE], mode=STRSPE)
    if GENERIC in dict_info:
        return __parse_dataset(dict_info[GENERIC], mode=GENERIC)
    if STRUCTURE in dict_info:
        return StructureParser().format_structures(
            dict_info[STRUCTURE][STRUCTURES]
        )
    if REG_INTERFACE in dict_info:
        return handle_registry_interface(dict_info)
    raise NotImplemented("Unsupported", "Cannot parse input as SDMX.")


def __parse_dataset(message_info: Dict[str, Any], mode: str) -> Dict[str, Any]:
    """Parse dataset.

    Args:
        message_info: Dict.
        mode: Str.

    Returns:
        A dictionary of datasets.
    """
    str_info = __extract_structure(message_info[HEADER][STRUCTURE])
    dataset_info = add_list(message_info[DATASET])
    datasets = {}
    for dataset in dataset_info:
        ds = create_dataset(dataset, str_info, mode)
        datasets[ds.short_urn] = ds
    return datasets
