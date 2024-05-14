"""Writer auxiliary functions."""

from collections import OrderedDict
from datetime import datetime
from typing import Any, Dict

from pysdmx.model.message import ActionType, MessageType

MESSAGE_TYPE_MAPPING = {
    MessageType.GenericDataSet: "GenericData",
    MessageType.StructureSpecificDataSet: "StructureSpecificData",
    MessageType.Metadata: "Structure",
}

ABBR_MSG = "mes"
ABBR_GEN = "gen"
ABBR_COM = "com"
ABBR_STR = "str"
ABBR_SPE = "ss"

ANNOTATIONS = "Annotations"
STRUCTURES = "Structures"
ORGS = "OrganisationSchemes"
AGENCIES = "AgencyScheme"
CODELISTS = "Codelists"
CONCEPTS = "Concepts"
DSDS = "DataStructures"
DATAFLOWS = "Dataflows"
CONSTRAINTS = "Constraints"

BASE_URL = "http://www.sdmx.org/resources/sdmxml/schemas/v2_1"

NAMESPACES = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    ABBR_MSG: f"{BASE_URL}/message",
    ABBR_GEN: f"{BASE_URL}/generic",
    ABBR_COM: f"{BASE_URL}/common",
    ABBR_STR: f"{BASE_URL}/structure",
    ABBR_SPE: f"{BASE_URL}/structureSpecific",
}

URN_DS_BASE = "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure="


def __namespaces_from_type(type_: MessageType) -> str:
    """Returns the namespaces for the XML file based on type.

    Args:
        type_: MessageType to be used

    Returns:
        A string with the namespaces
    """
    if type_ == MessageType.GenericDataSet:
        return f"xmlns:{ABBR_GEN}={NAMESPACES[ABBR_GEN]!r} "
    elif type_ == MessageType.StructureSpecificDataSet:
        return f"xmlns:{ABBR_SPE}={NAMESPACES[ABBR_SPE]!r} "
    elif type_ == MessageType.Metadata:
        return f"xmlns:{ABBR_STR}={NAMESPACES[ABBR_STR]!r} "
    else:
        return ""


def __namespaces_from_content(content: Dict[str, Any]) -> str:
    """Returns the namespaces for the XML file based on content.

    Args:
        content: Datasets or None

    Returns:
        A string with the namespaces

    Raises:
        Exception: If the dataset has no structure defined
    """
    outfile = ""
    for i, key in enumerate(content):
        if content[key].structure is None:
            raise Exception(f"Dataset {key} has no structure defined")
        ds_urn = URN_DS_BASE
        ds_urn += (
            f"{content[key].structure.unique_id}:"
            f"ObsLevelDim:{content[key].dim_at_obs}"
        )
        outfile += f"xmlns:ns{i}={ds_urn!r}"
    return outfile


def create_namespaces(
    type_: MessageType, content: Dict[str, Any], prettyprint: bool = False
) -> str:
    """Creates the namespaces for the XML file.

    Args:
        type_: MessageType to be used
        content: Datasets or None
        prettyprint: Prettyprint or not

    Returns:
        A string with the namespaces
    """
    nl = "\n" if prettyprint else ""

    outfile = f'<?xml version="1.0" encoding="UTF-8"?>{nl}'

    outfile += f"<{ABBR_MSG}:{MESSAGE_TYPE_MAPPING[type_]} "
    outfile += f'xmlns:xsi={NAMESPACES["xsi"]!r} '
    outfile += f"xmlns:{ABBR_MSG}={NAMESPACES[ABBR_MSG]!r} "
    outfile += __namespaces_from_type(type_)
    if type_ == MessageType.StructureSpecificDataSet:
        outfile += __namespaces_from_content(content)
    outfile += (
        f"xmlns:{ABBR_COM}={NAMESPACES[ABBR_COM]!r} "
        f'xsi:schemaLocation="{NAMESPACES[ABBR_MSG]} '
        f'https://registry.sdmx.org/schemas/v2_1/SDMXMessage.xsd">'
    )

    return outfile


DEFAULT_HEADER = {
    "ID": "test",
    "Test": "true",
    "Prepared": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
    "Sender": "Unknown",
    "Receiver": "Not_Supplied",
    "DataSetAction": ActionType.Information.value,
    "Source": "PySDMX",
}


def __generate_value_element(element: str, prettyprint: bool) -> str:
    """Generates a value element for the XML file (XML tag with value).

    Args:
        element: ID, Test, Prepared, Sender, Receiver, DataSetAction, Source
        prettyprint: Prettyprint or not

    Returns:
        A string with the value element
    """
    nl = "\n" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""
    return (
        f"{nl}{child2}<{ABBR_MSG}:{element}>"
        f"{DEFAULT_HEADER[element]}"
        f"</{ABBR_MSG}:{element}>"
    )


def __generate_item_element(element: str, prettyprint: bool) -> str:
    """Generates an item element for the XML file (XML tag with id attribute).

    Args:
        element: Sender, Receiver
        prettyprint: Prettyprint or not

    Returns:
        A string with the item element
    """
    nl = "\n" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""
    return (
        f"{nl}{child2}<{ABBR_MSG}:{element} id={DEFAULT_HEADER[element]!r}/>"
    )


def __generate_structure_element(
    content: Dict[str, Any], prettyprint: bool
) -> str:
    return ""


def generate_new_header(
    type_: MessageType, datasets: Dict[str, Any], prettyprint: bool
) -> str:
    """Writes the header to the XML file.

    Args:
        type_: MessageType to be used
        datasets: Datasets or None
        prettyprint: Prettyprint or not

    Returns:
        A string with the header

    Raises:
        NotImplementedError: If the MessageType is not Metadata
    """
    if type_ != MessageType.Metadata:
        raise NotImplementedError("Only Metadata messages are supported")

    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""

    outfile = f"{nl}{child1}<{ABBR_MSG}:Header>"
    outfile += __generate_value_element("ID", prettyprint)
    outfile += __generate_value_element("Test", prettyprint)
    outfile += __generate_value_element("Prepared", prettyprint)
    outfile += __generate_item_element("Sender", prettyprint)
    outfile += __generate_item_element("Receiver", prettyprint)
    if type_.value < MessageType.Metadata.value:
        outfile += __generate_structure_element(datasets, prettyprint)
        outfile += __generate_value_element("DataSetAction", prettyprint)
    outfile += __generate_value_element("Source", prettyprint)
    outfile += f"{nl}{child1}</{ABBR_MSG}:Header>"
    return outfile


def __write_metadata_element(
    package: Dict[str, Any], key: str, prettyprint: object
) -> str:
    """Writes the metadata element to the XML file.

    Args:
        package: The package to be written
        key: The key to be used
        prettyprint: Prettyprint or not

    Returns:
        A string with the metadata element
    """
    outfile = ""
    nl = "\n" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""

    if key in package:
        outfile += f"{nl}{child2}<{ABBR_STR}:{MSG_CONTENT_PKG[key]}>"
        for item in package[key].values():
            outfile += item._to_XML(f"{nl}{child2}")
        outfile += f"{nl}{child2}</{ABBR_STR}:{MSG_CONTENT_PKG[key]}>"

    return outfile


MSG_CONTENT_PKG = OrderedDict(
    [
        (ORGS, "OrganisationSchemes"),
        (DATAFLOWS, "Dataflows"),
        (CODELISTS, "Codelists"),
        (CONCEPTS, "Concepts"),
        (DSDS, "DataStructures"),
        (CONSTRAINTS, "ContentConstraints"),
    ]
)


MSG_CONTENT_ITEM = {
    ORGS: "AgencyScheme",
    DATAFLOWS: "Dataflow",
    CODELISTS: "Codelist",
    CONCEPTS: "ConceptScheme",
    DSDS: "DataStructure",
    CONSTRAINTS: "ContentConstraint",
}


def generate_structures(content: Dict[str, Any], prettyprint: bool) -> str:
    """Writes the structures to the XML file.

    Args:
        content: The Message Content to be written
        prettyprint: Prettyprint or not

    Returns:
        A string with the structures
    """
    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""

    outfile = f"{nl}{child1}<{ABBR_MSG}:Structures>"

    for key in MSG_CONTENT_PKG:
        outfile += __write_metadata_element(content, key, prettyprint)

    outfile += f"{nl}{child1}</{ABBR_MSG}:Structures>"

    return outfile


def get_end_message(type_: MessageType, prettyprint: bool) -> str:
    """Returns the end message for the XML file.

    Args:
        type_: MessageType to be used
        prettyprint: Prettyprint or not

    Returns:
        A string with the end message
    """
    nl = "\n" if prettyprint else ""
    return f"{nl}</{ABBR_MSG}:{MESSAGE_TYPE_MAPPING[type_]}>"


def add_indent(indent: str) -> str:
    """Adds another indent.

    Args:
        indent: The string to be indented

    Returns:
        A string with one more indentation
    """
    return indent + "\t"


def get_outfile(obj_: Dict[str, Any], key: str = "", indent: str = "") -> str:
    """Generates an outfile from the object.

    Args:
        obj_: The object to be used
        key: The key to be used
        indent: The indentation to be used

    Returns:
        A string with the outfile

    """
    element = obj_.get(key) or []

    return "".join(element)


def export_intern_data(data: Dict[str, Any], indent: str) -> str:
    """Export internal data (Annotations, Name, Description) on the XML file.

    Args:
        data: Information to be exported
        indent: Indentation used

    Returns:
        The XML string with the exported data
    """
    outfile = get_outfile(data, "Annotations", indent)
    outfile += get_outfile(data, "Name", indent)
    outfile += get_outfile(data, "Description", indent)

    return outfile
