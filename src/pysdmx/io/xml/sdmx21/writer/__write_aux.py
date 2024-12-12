# mypy: disable-error-code="union-attr"
"""Writer auxiliary functions."""

from collections import OrderedDict
from typing import Dict, List, Optional, Tuple

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.enums import MessageType
from pysdmx.model.dataset import Dataset
from pysdmx.model.message import Header
from pysdmx.util import parse_short_urn

MESSAGE_TYPE_MAPPING = {
    MessageType.GenericDataSet: "GenericData",
    MessageType.StructureSpecificDataSet: "StructureSpecificData",
    MessageType.Structure: "Structure",
    MessageType.Error: "Error",
    MessageType.Submission: "RegistryInterface",
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
ALL_DIM = "AllDimensions"

BASE_URL = "http://www.sdmx.org/resources/sdmxml/schemas/v2_1"

NAMESPACES = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    ABBR_MSG: f"{BASE_URL}/message",
    ABBR_GEN: f"{BASE_URL}/data/generic",
    ABBR_COM: f"{BASE_URL}/common",
    ABBR_STR: f"{BASE_URL}/structure",
    ABBR_SPE: f"{BASE_URL}/data/structurespecific",
}

URN_DS_BASE = "urn:sdmx:org.sdmx.infomodel.datastructure.DataStructure="


def __namespaces_from_type(type_: MessageType) -> str:
    """Returns the namespaces for the XML file based on type.

    Args:
        type_: MessageType to be used

    Returns:
        A string with the namespaces

    Raises:
        NotImplemented: If the MessageType is not implemented
    """
    if type_ == MessageType.Structure:
        return f"xmlns:{ABBR_STR}={NAMESPACES[ABBR_STR]!r} "
    elif type_ == MessageType.StructureSpecificDataSet:
        return f"xmlns:{ABBR_SPE}={NAMESPACES[ABBR_SPE]!r} "
    elif type_ == MessageType.GenericDataSet:
        return f"xmlns:{ABBR_GEN}={NAMESPACES[ABBR_GEN]!r} "
    else:
        raise NotImplemented(f"{type_} not implemented")


def create_namespaces(
    type_: MessageType, ss_namespaces: str, prettyprint: bool = False
) -> str:
    """Creates the namespaces for the XML file.

    Args:
        type_: MessageType to be used
        ss_namespaces: The namespaces for the StructureSpecificData
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
        f"{ss_namespaces}"
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


def __write_header(header: Header, prettyprint: bool) -> str:
    """Writes the Header part of the message.

    Args:
        header: The Header to be written
        prettyprint: Prettyprint or not

    Returns:
        The XML string
    """

    def __value(element: str, value: Optional[str]) -> str:
        """Generates a value element for the XML file.

        A Value element is an XML tag with a value.

        Args:
            element: ID, Test, Prepared, Sender, Receiver, Source
            value: The value to be written

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

    def __item(element: str, id_: Optional[str]) -> str:
        """Generates an item element for the XML file.

        An Item element is an XML tag with an id attribute.

        Args:
            element: Sender, Receiver
            id_: The ID to be written

        Returns:
            A string with the item element
        """
        if not id_:
            return ""
        nl = "\n" if prettyprint else ""
        child2 = "\t\t" if prettyprint else ""
        return f"{nl}{child2}<{ABBR_MSG}:{element} id={id_!r}/>"

    def __reference(urn_structure: str, dimension: str) -> str:
        nl = "\n" if prettyprint else ""
        child2 = "\t\t" if prettyprint else ""
        child3 = "\t\t\t" if prettyprint else ""
        child4 = "\t\t\t\t" if prettyprint else ""

        reference = parse_short_urn(urn_structure)
        namespace = (
            f"{URN_DS_BASE}={reference.agency}:{reference.id}"
            f"({reference.version})"
        )

        return (
            # First the message structure
            f"{nl}{child2}<{ABBR_MSG}:Structure "
            f"structureID={reference.id!r} "
            f"namespace={namespace!r} "
            f"dimensionAtObservation={dimension!r}>"
            # Then the common structure
            f"{nl}{child3}<{ABBR_COM}:Structure>"
            # Then the reference
            f"{nl}{child4}<Ref agencyID={reference.agency!r} "
            f"id={reference.id!r} version={reference.version!r} "
            f"class={reference.sdmx_type!r}/>"
            # Close the common structure
            f"{nl}{child3}</{ABBR_COM}:Structure>"
            # Close the message structure
            f"{nl}{child2}</{ABBR_MSG}:Structure>"
        )

    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""
    prepared = header.prepared.strftime("%Y-%m-%dT%H:%M:%S")
    test = str(header.test).lower()
    references_str = ""
    if header.dataset_references is not None:
        for short_urn, dim_at_obs in header.dataset_references.items():
            references_str += __reference(short_urn, dim_at_obs)
    return (
        f"{nl}{child1}<{ABBR_MSG}:Header>"
        f"{__value('ID', header.id)}"
        f"{__value('Test', test)}"
        f"{__value('Prepared', prepared)}"
        f"{__item('Sender', header.sender)}"
        f"{__item('Receiver', header.receiver)}"
        f"{__value('Source', header.source)}"
        f"{references_str}"
        f"{nl}{child1}</{ABBR_MSG}:Header>"
    ).replace("'", '"')


# ------------------
# -- DATA WRITING --
# ------------------

CHUNKSIZE = 100000


def get_structure(dataset: Dataset) -> str:
    """This function gets the structure of a dataset.

    Args:
        dataset: The dataset to get the structure from

    Returns:
        The structure Short URN
    """
    if isinstance(dataset.structure, str):
        return dataset.structure
    return dataset.structure.short_urn


def remove_null_values_on_dataset(dataset: PandasDataset) -> PandasDataset:
    """This function removes null values from a dataset.

    Args:
        dataset: The dataset to remove null values from

    Returns:
        The dataset without null values
    """
    dataset.data = dataset.data.fillna(value="")
    return dataset


def get_codes(
    dimension_code: str, dataset: PandasDataset
) -> Tuple[List[str], List[str]]:
    """This function gets the types and codes of a dataset."""
    series_codes = []
    obs_codes = [dimension_code, dataset.structure.components.measures[0].id]

    for dim in dataset.structure.components.dimensions:
        if dim.id != dimension_code:
            series_codes.append(dim.id)

    for att in dataset.structure.components.attributes:
        if att.attachment_level == "O":
            obs_codes.append(att.id)
        elif att.attachment_level == "D":
            series_codes.append(att.id)

    series_codes = [
        x
        for x in series_codes
        if x not in obs_codes and x in dataset.data.columns
    ]
    obs_codes = [x for x in obs_codes if x in dataset.data.columns]

    return series_codes, obs_codes


def check_content_dataset(content: Dict[str, PandasDataset]) -> None:
    """This function checks if the content is a dataset."""
    for dataset in content.values():
        if not isinstance(dataset, PandasDataset):
            raise Invalid("Message Content must be a dataset")
