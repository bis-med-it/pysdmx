from typing import Any, Dict

import xmltodict

from pysdmx.io.xml.doc_validation import validate_doc

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

XML_OPTIONS_21 = {
    "process_namespaces": True,
    "namespaces": NAMESPACES_21,
    "dict_constructor": dict,
    "attr_prefix": "",
}
SCHEMA_ROOT_30 = "http://www.sdmx.org/resources/sdmxml/schemas/v3_0/"
NAMESPACES_30 = {
    SCHEMA_ROOT_30 + "message": None,
    SCHEMA_ROOT_30 + "common": None,
    SCHEMA_ROOT_30 + "structure": None,
    "http://www.w3.org/2001/XMLSchema-instance": "xsi",
    "http://www.w3.org/XML/1998/namespace": None,
    SCHEMA_ROOT_30 + "data/structurespecific": None,
    SCHEMA_ROOT_30 + "registry": None,
    "http://schemas.xmlsoap.org/soap/envelope/": None,
}

XML_OPTIONS_30 = {
    "process_namespaces": True,
    "namespaces": NAMESPACES_30,
    "dict_constructor": dict,
    "attr_prefix": "",
}


def parse_xml(
    input_str: str,
    validate: bool = True,
) -> Dict[str, Any]:
    """Reads SDMX-ML data and returns a dictionary with the parsed data.

    Args:
        input_str: SDMX-ML data to be parsed.
        validate: If True, the SDMX-ML data will be validated against the XSD.

    Returns:
        dict: Dictionary with the parsed data.

    Raises:
        Invalid: If the SDMX data cannot be parsed.
    """
    if validate:
        validate_doc(input_str)
    if SCHEMA_ROOT_30 in input_str:
        dict_info = xmltodict.parse(
            input_str,
            **XML_OPTIONS_30,  # type: ignore[arg-type]
        )
    else:
        dict_info = xmltodict.parse(
            input_str,
            **XML_OPTIONS_21,  # type: ignore[arg-type]
        )

    del input_str

    return dict_info
