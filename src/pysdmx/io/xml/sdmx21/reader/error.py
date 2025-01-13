"""SDMX 2.1 XML error reader."""

from typing import Any, Dict

from pysdmx.errors import Invalid
from pysdmx.io.xml.sdmx21.__tokens import (
    ERROR,
    ERROR_CODE,
    ERROR_MESSAGE,
    ERROR_TEXT,
)


def read(dict_info: Dict[str, Any]):
    """Reads an Error message from the SDMX-ML file and raises the exception.

    Args:
        dict_info: The dictionary with the error message.

    Raises:
        Invalid: Error message as exception.
    """
    code = dict_info[ERROR][ERROR_MESSAGE][ERROR_CODE]
    text = dict_info[ERROR][ERROR_MESSAGE][ERROR_TEXT]
    raise Invalid("Invalid", f"{code}: {text}")
