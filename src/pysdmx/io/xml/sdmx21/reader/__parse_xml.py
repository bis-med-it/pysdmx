from typing import Any, Dict

import xmltodict

from pysdmx.io.xml.sdmx21.reader.doc_validation import validate_doc

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


def parse_xml(
    infile: str,
    validate: bool = True,
) -> Dict[str, Any]:
    """Reads an SDMX-ML file and returns a dictionary with the parsed data.

    Args:
        infile: Path to file, URL, or string.
        validate: If True, the XML data will be validated against the XSD.

    Returns:
        dict: Dictionary with the parsed data.

    Raises:
        Invalid: If the SDMX data cannot be parsed.
    """
    if validate:
        validate_doc(infile)
    dict_info = xmltodict.parse(
        infile,
        **XML_OPTIONS,  # type: ignore[arg-type]
    )

    del infile

    return dict_info
