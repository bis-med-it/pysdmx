# mypy: disable-error-code="union-attr"
"""Writer auxiliary functions."""

from collections import OrderedDict
from typing import Dict, List, Optional, Sequence, Tuple

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io.format import Format
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Role, Schema
from pysdmx.model.dataset import Dataset
from pysdmx.model.message import Header
from pysdmx.util import parse_short_urn

MESSAGE_TYPE_MAPPING = {
    Format.DATA_SDMX_ML_2_1_GEN: "GenericData",
    Format.DATA_SDMX_ML_2_1_STR: "StructureSpecificData",
    Format.STRUCTURE_SDMX_ML_2_1: "Structure",
    Format.ERROR_SDMX_ML_2_1: "Error",
    Format.REGISTRY_SDMX_ML_2_1: "RegistryInterface",
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


def __namespaces_from_type(type_: Format) -> str:
    """Returns the namespaces for the XML file based on type.

    Args:
        type_: MessageType to be used

    Returns:
        A string with the namespaces

    Raises:
        NotImplemented: If the MessageType is not implemented
    """
    if type_ == Format.STRUCTURE_SDMX_ML_2_1:
        return f"xmlns:{ABBR_STR}={NAMESPACES[ABBR_STR]!r} "
    elif type_ == Format.DATA_SDMX_ML_2_1_STR:
        return f"xmlns:{ABBR_SPE}={NAMESPACES[ABBR_SPE]!r} "
    elif type_ == Format.DATA_SDMX_ML_2_1_GEN:
        return f"xmlns:{ABBR_GEN}={NAMESPACES[ABBR_GEN]!r} "
    else:
        raise NotImplemented(f"{type_} not implemented")


def create_namespaces(
    type_: Format, ss_namespaces: str = "", prettyprint: bool = False
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


def get_end_message(type_: Format, prettyprint: bool) -> str:
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


def __write_header(
    header: Header, prettyprint: bool, add_namespace_structure: bool = False
) -> str:
    """Writes the Header part of the message.

    Args:
        header: The Header to be written
        prettyprint: Prettyprint or not
        add_namespace_structure: Add the namespace for the structure

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
        child2 = "\t\t" if prettyprint else ""
        return f"{nl}{child2}<{ABBR_MSG}:{element} id={id_!r}/>"

    def __reference(urn_structure: str, dimension: str) -> str:
        child2 = "\t\t" if prettyprint else ""
        child3 = "\t\t\t" if prettyprint else ""
        child4 = "\t\t\t\t" if prettyprint else ""
        namespace = ""
        reference = parse_short_urn(urn_structure)
        if add_namespace_structure:
            namespace = (
                f"{URN_DS_BASE}={reference.agency}:{reference.id}"
                f"({reference.version})"
            )
            namespace = f"namespace={namespace!r} "

        return (
            # First the message structure
            f"{nl}{child2}<{ABBR_MSG}:Structure "
            f"structureID={reference.id!r} "
            f"{namespace}"
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
    action_value = (
        header.dataset_action.value if header.dataset_action else None
    )
    if header.structure is not None:
        for short_urn, dim_at_obs in header.structure.items():
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
        f"{__value('DataSetAction', action_value)}"
        f"{__value('DataSetID', header.dataset_id)}"
        f"{nl}{child1}</{ABBR_MSG}:Header>"
    ).replace("'", '"')


# ------------------
# -- DATA WRITING --
# ------------------


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


def get_codes(
    dimension_code: str, dataset: PandasDataset
) -> Tuple[List[str], List[str]]:
    """This function divides the components in Series and Obs."""
    series_codes = []
    obs_codes = [dimension_code, dataset.structure.components.measures[0].id]

    # Getting the series and obs codes
    for dim in dataset.structure.components.dimensions:
        if dim.id != dimension_code:
            series_codes.append(dim.id)

    # Adding the attributes based on the attachment level
    for att in dataset.structure.components.attributes:
        if att.attachment_level == "O":
            obs_codes.append(att.id)
        elif att.attachment_level is not None and att.attachment_level != "D":
            series_codes.append(att.id)

    return series_codes, obs_codes


def check_content_dataset(content: Sequence[PandasDataset]) -> None:
    """Checks if the Message content is a dataset."""
    if not all(isinstance(dataset, PandasDataset) for dataset in content):
        raise Invalid("Message Content must only contain a Dataset sequence.")


def check_dimension_at_observation(
    content: Dict[str, PandasDataset],
    dimension_at_observation: Optional[Dict[str, str]],
) -> Dict[str, str]:
    """This function checks if the dimension at observation is valid."""
    # If dimension_at_observation is None, set it to ALL_DIM
    if dimension_at_observation is None:
        dimension_at_observation = dict.fromkeys(content, ALL_DIM)
        return dimension_at_observation
    # Validate the datasets
    for ds in content.values():
        writing_validation(ds)
    # Check the datasets and their dimensions are present
    for key, value in dimension_at_observation.items():
        if key not in content:
            raise Invalid(f"Dataset {key} not found in Message content.")
        dimension_codes = [
            dim.id for dim in content[key].structure.components.dimensions
        ]
        if value not in dimension_codes:
            raise Invalid(
                f"Dimension at observation {value} "
                f"not found in dataset {key}."
            )
    # Add the missing datasets on mapping with ALL_DIM
    for key in content:
        if key not in dimension_at_observation:
            dimension_at_observation[key] = ALL_DIM
    return dimension_at_observation


def writing_validation(dataset: PandasDataset) -> None:
    """Structural validation of the dataset."""
    if not isinstance(dataset.structure, Schema):
        raise Invalid(
            "Dataset Structure is not a Schema. Cannot perform operation."
        )
    required_components = [
        comp.id
        for comp in dataset.structure.components
        if comp.role in (Role.DIMENSION, Role.MEASURE)
    ]
    for att in dataset.structure.components.attributes:
        if (
            att.required
            and att.attachment_level is not None
            and att.attachment_level != "D"
        ):
            required_components.append(att.id)
    non_required = [
        comp.id
        for comp in dataset.structure.components
        if comp.id not in required_components
    ]
    # Columns match components
    columns = dataset.data.columns
    all_components = required_components + non_required
    difference = [col for col in columns if col not in all_components]

    for comp in required_components:
        difference.append(comp) if comp not in columns else None
    if difference:
        raise Invalid(
            f"Data columns must match components. "
            f"Difference: {', '.join(difference)}"
        )
    # Check if the dataset has at least one dimension and one measure
    if not dataset.structure.components.dimensions:
        raise Invalid(
            "The dataset structure must have at least one dimension."
        )
    if not dataset.structure.components.measures:
        raise Invalid("The dataset structure must have at least one measure.")


def __to_camel_case(snake_str: str) -> str:
    return "".join(x.capitalize() for x in snake_str.lower().split("_"))


def __to_lower_camel_case(snake_str: str) -> str:
    # We capitalize the first letter of each component except the first one
    # with the 'capitalize' method and join them together.
    camel_string = __to_camel_case(snake_str)
    return snake_str[0].lower() + camel_string[1:]
