"""Utility functions and constants for the parsers module."""

from typing import Any, Dict, List

# Common
ID = "id"
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
STR_URL_LOW = "structure_url"
SER_URL = "serviceURL"
SER_URL_LOW = "service_url"
IS_EXTERNAL_REF = "isExternalReference"
IS_EXTERNAL_REF_LOW = "is_external_reference"
IS_FINAL = "isFinal"
IS_FINAL_LOW = "is_final"
IS_PARTIAL = "isPartial"
IS_PARTIAL_LOW = "is_partial"
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
URIS = "uris"
EMAILS = "emails"
TELEPHONES = "telephones"
FAXES = "faxes"
URI = "URI"
EMAIL = "Email"
X400 = "X400"
TELEPHONE = "Telephone"
FAX = "Fax"

# Extras
AGENCY = "Agency"
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

FacetType = {
    "minLength": "min_length",
    "maxLength": "max_length",
    "minValue": "min_value",
    "maxValue": "max_value",
    "startValue": "start_value",
    "endValue": "end_value",
    "interval": "interval",
    "timeInterval": "time_interval",
    "decimals": "decimals",
    "pattern": "pattern",
    "startTime": "start_time",
    "endTime": "end_time",
    "isSequence": "is_sequence",
}


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
