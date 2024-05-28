"""Parsing configuration for SDMX-ML 2.1 messages."""

SCHEMA_ROOT = "http://www.sdmx.org/resources/sdmxml/schemas/v2_1/"
NAMESPACES_21 = {
    SCHEMA_ROOT + "message": None,
    SCHEMA_ROOT + "common": None,
    SCHEMA_ROOT + "structure": None,
    "http://www.w3.org/2001/XMLSchema-instance": "xsi",
    "http://www.w3.org/XML/1998/namespace": None,
    SCHEMA_ROOT + "data/structurespecific": None,
    SCHEMA_ROOT + "data/generic": None,
    SCHEMA_ROOT + "registry": None,
    "http://schemas.xmlsoap.org/soap/envelope/": None,
}

XML_OPTIONS = {
    "process_namespaces": True,
    "namespaces": NAMESPACES_21,
    "dict_constructor": dict,
    "attr_prefix": "",
}

# Common
HEADER = "Header"
DATASET = "DataSet"
SERIES = "Series"
OBS = "Obs"
AGENCY_ID = "agencyID"
ID = "id"
VERSION = "version"

# Structure Specific
STRSPE = "StructureSpecificData"
GENERIC = "GenericData"
SERIESKEY = "SeriesKey"
ATTRIBUTES = "Attributes"
VALUE = "Value"
OBS_DIM = "ObsDimension"
OBSVALUE = "ObsValue"
OBSKEY = "ObsKey"
# Header
STRREF = "structureRef"
STRUCTURE = "Structure"
STR_USAGE = "StructureUsage"
STRID = "structureID"
STRTYPE = "structure_type"
DIM_OBS = "dimensionAtObservation"
ALL_DIM = "AllDimensions"
REF = "Ref"
DATASET_ID = "DataSetID"

# SDMX Error handling
ERROR = "Error"
ERROR_MESSAGE = "ErrorMessage"
ERROR_CODE = "code"
ERROR_TEXT = "Text"

# SDMX Registry Interface handling
REG_INTERFACE = "RegistryInterface"
SUBMIT_STRUCTURE_RESPONSE = "SubmitStructureResponse"
SUBMISSION_RESULT = "SubmissionResult"
SUBMITTED_STRUCTURE = "SubmittedStructure"
MAINTAINABLE_OBJECT = "MaintainableObject"
ACTION = "action"
STATUS_MSG = "StatusMessage"
STATUS = "status"

# SOAP API handling
FAULT = "Fault"
FAULTCODE = "faultcode"
FAULTSTRING = "faultstring"


# Structures
# Common
NAME = "Name"
DESC = "Description"
LANG = "lang"
XML_TEXT = "#text"
STR_URL = "structureURL"
STR_URL_LOW = "structureUrl"
SER_URL = "serviceURL"
SER_URL_LOW = "serviceUrl"
# General
ANNOTATIONS = "Annotations"
STRUCTURES = "Structures"
ORGS = "OrganisationSchemes"
AGENCIES = "AgencyScheme"
CODELISTS = "Codelists"
CONCEPTS = "Concepts"
DSDS = "DataStructures"
DATAFLOWS = "Dataflows"
CONSTRAINTS = "Constraints"

# Individual
AGENCY = "Agency"
CL = "Codelist"
CODE = "Code"
CS = "ConceptScheme"
CS_LOW = "concept_scheme"
CON = "Concept"
DSD = "DataStructure"

# DSD components
DSD_COMPS = "DataStructureComponents"
CON_ID = "ConceptIdentity"
CON_ID_LOW = "concept_identity"
CON_ROLE = "ConceptRole"
CON_ROLE_LOW = "concept_role"
# Dimension
DIM_LIST = "DimensionList"
DIM_LIST_LOW = "dimension_list"
DIM = "Dimension"
TIME_DIM = "TimeDimension"
# Attribute
ATT_LIST = "AttributeList"
ATT_LIST_LOW = "attribute_list"
ATT = "Attribute"
ATT_REL = "AttributeRelationship"
AS_STATUS = "assignmentStatus"
# Measure
ME_LIST = "MeasureList"
ME_LIST_LOW = "measure_list"
MEASURE = "Measure"
PRIM_MEASURE = "PrimaryMeasure"
# Group Dimension
GROUP = "Group"
GROUP_DIM_LOW = "group_dimension_descriptor"
GROUP_DIM = "GroupDimension"
DIM_REF = "DimensionReference"

# Dataflows
DF = "Dataflow"

# Constraints
CON_CONS = "ContentConstraint"
CONS_ATT = "ConstraintAttachment"
CUBE_REGION = "CubeRegion"
CONTENT_REGION = "dataContentRegion"
KEY = "Key"
KEY_VALUE = "KeyValue"
DATA_KEY_SET = "DataKeySet"
DATA_KEY_SET_LOW = "dataKeySet"
INCLUDED = "isIncluded"
INCLUDE = "include"

# Annotation
ANNOTATION = "Annotation"
ANNOTATION_TITLE = "AnnotationTitle"
ANNOTATION_TYPE = "AnnotationType"
ANNOTATION_TEXT = "AnnotationText"
ANNOTATION_URL = "AnnotationURL"

TITLE = "title"
TYPE_ = "type_"
TYPE = "type"
TEXT = "text"
URL = "url"
URN = "URN"

# Representation
CORE_REP = "CoreRepresentation"
CORE_REP_LOW = "core_representation"
LOCAL_REP = "LocalRepresentation"
LOCAL_REP_LOW = "local_representation"
ENUM = "Enumeration"
ENUM_FORMAT = "EnumerationFormat"
TEXT_FORMAT = "TextFormat"

# Facets
FACETS = "facets"
TEXT_TYPE = "textType"
TEXT_TYPE_LOW = "text_type"

# Contact
CONTACT = "Contact"
DEPARTMENT = "Department"
ROLE = "Role"
URI = "URI"
EMAIL = "Email"
X400 = "X400"
TELEPHONE = "Telephone"
FAX = "Fax"

# Extras
MAINTAINER = "maintainer"
XMLNS = "xmlns"
COMPS = "components"
PARENT = "Parent"
PAR_ID = "maintainableParentID"
PAR_VER = "maintainableParentVersion"
REL_TO = "relatedTo"
NO_REL = "NoSpecifiedRelationship"

# To exclude from attached_attributes
exc_attributes = [STRREF, "action", "dataScope", "xsi:type", SERIES, OBS]

# Content types
DATASTRUCTURES_CM = "DataStructures"
DATAFLOWS_CM = "Dataflows"
CODELISTS_CM = "Codelists"
CONCEPTS_CM = "Concepts"
ORGANISATIONSCHEMES_CM = "OrganisationSchemes"
