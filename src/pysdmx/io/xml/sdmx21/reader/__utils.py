"""Utility functions and constants for the parsers module."""

from typing import Any, Dict, List

# Common
ID = "ID"
AGENCY_ID = "agencyID"
XMLNS = "xmlns"
VERSION = "version"

# Structure Specific
VALUE = "Value"

# Header
REF = "Ref"

# Structures
# Common
NAME = "Name"
DESC = "Description"
STR_URL = "structureURL"
STR_URL_LOW = "structureUrl"
SER_URL = "serviceURL"
SER_URL_LOW = "serviceUrl"
# General
ANNOTATIONS = "Annotations"

# Individual
CL = "Codelist"
CON = "Concept"

# Dimension
DIM = "Dimension"

# Measure
PRIM_MEASURE = "PrimaryMeasure"

# Group Dimension
GROUP = "Group"
DIM_REF = "DimensionReference"

# Constraints
KEY_VALUE = "KeyValue"

# Annotation
ANNOTATION = "Annotation"
ANNOTATION_TITLE = "AnnotationTitle"
ANNOTATION_TYPE = "AnnotationType"
ANNOTATION_TEXT = "AnnotationText"
ANNOTATION_URL = "AnnotationURL"

TITLE = "title"
TEXT = "text"
TYPE = "type"
URL = "url"

# Facets
FACETS = "facets"
TEXT_TYPE = "textType"
TEXT_TYPE_LOW = "text_type"

# Contact
CONTACT = "Contact"
DEPARTMENT = "Department"
ROLE = "Role"
URIS = "URIs"
EMAILS = "Emails"
TELEPHONES = "Telephones"
FAXES = "Faxes"
URI = "URI"
EMAIL = "Email"
X400 = "X400"
TELEPHONE = "Telephone"
FAX = "Fax"

# Extras
AGENCY = "agency"
PAR_ID = "maintainableParentID"
PAR_VER = "maintainableParentVersion"

# Errors
missing_rep: Dict[str, List[Any]] = {"CON": [], "CS": [], "CL": []}
dsd_id: str = ""

# Structure types
AGENCIES = "AgencyScheme"
ORGS = "OrganisationSchemes"
CLS = "Codelists"
CONCEPTS = "ConceptSchemes"
CS = "ConceptScheme"
CODE = "Code"

FacetType = [
    "min_length",
    "max_length",
    "min_value",
    "max_value",
    "start_value",
    "end_value",
    "interval",
    "time_interval",
    "decimals",
    "pattern",
    "start_time",
    "end_time",
    "is_sequence",
]


def unique_id(agencyID: str, id_: str, version: str) -> str:
    """Create a unique ID for an object.

    Args:
        agencyID: The agency ID
        id_: The ID of the object
        version: The version of the object

    Returns:
        A string with the unique ID
    """
    return f"{agencyID}:{id_}({version})"


def add_list(element: Any) -> List[Any]:
    """Make sure an element is a list and convert it if it is not.

    Args:
        element: The element to be converted

    Returns:
        A list with the element
    """
    if not isinstance(element, list):
        element = [element]
    return element
