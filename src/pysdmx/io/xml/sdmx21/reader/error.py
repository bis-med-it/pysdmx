"""SDMX 2.1 XML error reader."""

from pysdmx.errors import Invalid
from pysdmx.io.xml.__parse_xml import parse_xml
from pysdmx.io.xml.__tokens import (
    ERROR,
    ERROR_CODE,
    ERROR_MESSAGE,
    ERROR_TEXT,
)


def read(input_str: str, validate: bool = True) -> None:
    """Reads an Error message from the SDMX-ML data and raises the exception.

    Args:
        input_str: The SDMX-ML data as a string.
        validate: If True, the input is validated before

    Raises:
        Invalid: Error message as exception.
    """
    dict_info = parse_xml(input_str, validate=validate)
    if ERROR not in dict_info:
        raise Invalid(
            "This SDMX document is not an SDMX-ML 2.1 Error message."
        )
    code = dict_info[ERROR][ERROR_MESSAGE][ERROR_CODE]
    text = dict_info[ERROR][ERROR_MESSAGE][ERROR_TEXT]
    raise Invalid("Invalid", f"{code}: {text}")
