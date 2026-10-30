"""Validates an SDMX-ML 2.1 XML file against the XSD schema."""

from io import BytesIO
from typing import List, Sequence

from lxml import etree
from sdmxschemas import SDMX_ML_21_MESSAGE_PATH as SCHEMA_PATH_21
from sdmxschemas import SDMX_ML_30_MESSAGE_PATH as SCHEMA_PATH_30
from sdmxschemas import SDMX_ML_31_MESSAGE_PATH as SCHEMA_PATH_31

from pysdmx.errors import Invalid
from pysdmx.io.xml.__allowed_lxml_errors import ALLOWED_ERRORS_CONTENT

SCHEMA_ROOT_30 = "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/"
SCHEMA_ROOT_31 = "http://www.sdmx.org/resources/sdmxml/schemas/v3_1/"


def sdmx_ml_version(head: str) -> str:
    """Returns the SDMX-ML version of a message.

    Args:
        head: The start of the message. Its first 1000 characters name
            the version.

    Returns:
        "3.1", "3.0" or "2.1".
    """
    check = head[:1000].lower()
    if SCHEMA_ROOT_31 in check:
        return "3.1"
    if SCHEMA_ROOT_30 in check:
        return "3.0"
    return "2.1"


def load_schema(head: str) -> etree.XMLSchema:
    """Loads the XSD schema of the SDMX-ML version of a message.

    Args:
        head: The start of the message. Its first 1000 characters name
            the version.

    Returns:
        The XSD schema of the SDMX-ML message.
    """
    path = {"3.1": SCHEMA_PATH_31, "3.0": SCHEMA_PATH_30}.get(
        sdmx_ml_version(head), SCHEMA_PATH_21
    )
    return etree.XMLSchema(etree.parse(path))


def severe_errors(messages: Sequence[str]) -> List[str]:
    """Filters out the XSD validation errors that pysdmx allows.

    Args:
        messages: The messages of the XSD validation errors.

    Returns:
        The messages of the other errors, in the same order.
    """
    severe = list(messages)
    for message in messages:
        for allowed_error in ALLOWED_ERRORS_CONTENT:
            if allowed_error in message:
                severe.remove(message)
    return severe


def validate_doc(input_str: str) -> None:
    """Validates the SDMX-ML data against the XSD schema for SDMX-ML.

    Args:
        input_str: The SDMX-ML data to validate.

    Raises:
        Invalid: If the SDMX-ML data does not validate against the schema.
    """
    parser = etree.ETCompatXMLParser(resolve_entities="internal")
    xmlschema = load_schema(input_str)

    bytes_infile = BytesIO(bytes(input_str, "UTF_8"))

    doc = etree.parse(bytes_infile, parser=parser)
    if not xmlschema.validate(doc):
        log_errors = list(xmlschema.error_log)  # type: ignore[call-overload]
        errors = severe_errors([e.message for e in log_errors])
        if len(errors) > 0:
            raise Invalid("Validation Error", ";\n".join(errors))
