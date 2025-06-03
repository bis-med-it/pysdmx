"""Validates an SDMX-ML 2.1 XML file against the XSD schema."""

from io import BytesIO

from lxml import etree
from sdmxschemas import SDMX_ML_21_MESSAGE_PATH as SCHEMA_PATH_21
from sdmxschemas import SDMX_ML_30_MESSAGE_PATH as SCHEMA_PATH_30

from pysdmx.errors import Invalid
from pysdmx.io.xml.__allowed_lxml_errors import ALLOWED_ERRORS_CONTENT

SCHEMA_ROOT_30 = "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/"


def validate_doc(input_str: str) -> None:
    """Validates the SDMX-ML data against the XSD schema for SDMX-ML 2.1.

    Args:
        input_str: The SDMX-ML data to validate.

    Raises:
        Invalid: If the SDMX-ML data does not validate against the schema.
    """
    parser = etree.ETCompatXMLParser()
    check = input_str[:1000].lower()
    if SCHEMA_ROOT_30 in check:
        xmlschema_doc = etree.parse(SCHEMA_PATH_30)
    else:
        xmlschema_doc = etree.parse(SCHEMA_PATH_21)

    xmlschema = etree.XMLSchema(xmlschema_doc)

    bytes_infile = BytesIO(bytes(input_str, "UTF_8"))

    doc = etree.parse(bytes_infile, parser=parser)
    if not xmlschema.validate(doc):
        log_errors = list(xmlschema.error_log)  # type: ignore[call-overload]
        unhandled_errors = []
        for e in log_errors:
            unhandled_errors.append(e.message)
        severe_errors = unhandled_errors.copy()
        for e in unhandled_errors:
            for allowed_error in ALLOWED_ERRORS_CONTENT:
                if allowed_error in e:
                    severe_errors.remove(e)

        if len(severe_errors) > 0:
            raise Invalid("Validation Error", ";\n".join(severe_errors))
