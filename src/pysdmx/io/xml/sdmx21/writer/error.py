"""Module for writing SDMX-ML 2.1 Error messages."""

from pysdmx.io.format import Format
from pysdmx.io.xml.__write_aux import __namespaces_from_type


def write() -> None:
    """Write data to SDMX-ML 2.1 Error format.

    Returns:
        The XML string if path is empty, None otherwise.
    """
    __namespaces_from_type(Format.ERROR_SDMX_ML_2_1)
