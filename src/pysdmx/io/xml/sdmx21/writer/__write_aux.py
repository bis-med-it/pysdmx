"""Writer auxiliary functions."""

from collections import OrderedDict
from typing import Any, Dict, Optional

from pysdmx.io.xml.enums import MessageType
from pysdmx.model.message import Header

MESSAGE_TYPE_MAPPING = {
    MessageType.GenericDataSet: "GenericData",
    MessageType.StructureSpecificDataSet: "StructureSpecificData",
    MessageType.Structure: "Structure",
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
    return f"xmlns:{ABBR_STR}={NAMESPACES[ABBR_STR]!r} "


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
    outfile += (
        f"xmlns:{ABBR_COM}={NAMESPACES[ABBR_COM]!r} "
        f'xsi:schemaLocation="{NAMESPACES[ABBR_MSG]} '
        f'https://registry.sdmx.org/schemas/v2_1/SDMXMessage.xsd">'
    )

    return outfile.replace("'", '"')


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


def __value(element: str, value: Optional[str], prettyprint: bool) -> str:
    """Generates a value element for the XML file.

    A Value element is an XML tag with a value.

    Args:
        element: ID, Test, Prepared, Sender, Receiver, Source
        value: The value to be written
        prettyprint: Prettyprint or not

    Returns:
        A string with the value element
    """
    if not value:
        return ""
    nl = "\n" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""
    return (
        f"{nl}{child2}<{ABBR_MSG}:{element}>"
        f"{value}"
        f"</{ABBR_MSG}:{element}>"
    )


def __item(element: str, id_: Optional[str], prettyprint: bool) -> str:
    """Generates an item element for the XML file.

    An Item element is an XML tag with an id attribute.

    Args:
        element: Sender, Receiver
        id_: The ID to be written
        prettyprint: Prettyprint or not

    Returns:
        A string with the item element
    """
    if not id_:
        return ""
    nl = "\n" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""
    return f"{nl}{child2}<{ABBR_MSG}:{element} id={id_!r}/>"


def __write_header(header: Header, prettyprint: bool) -> str:
    """Writes the Header part of the message.

    Args:
        header: The Header to be written
        prettyprint: Prettyprint or not

    Returns:
        The XML string
    """
    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""
    prepared = header.prepared.strftime("%Y-%m-%dT%H:%M:%S")
    test = str(header.test).lower()
    return (
        f"{nl}{child1}<{ABBR_MSG}:Header>"
        f"{__value('ID', header.id, prettyprint)}"
        f"{__value('Test', test, prettyprint)}"
        f"{__value('Prepared', prepared, prettyprint)}"
        f"{__item('Sender', header.sender, prettyprint)}"
        f"{__item('Receiver', header.receiver, prettyprint)}"
        f"{__value('Source', header.source, prettyprint)}"
        f"{nl}{child1}</{ABBR_MSG}:Header>"
    ).replace("'", '"')
