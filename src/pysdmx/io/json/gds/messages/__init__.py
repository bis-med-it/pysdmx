"""Module for SDMX-JSON GDS message schemas.

This module provides classes and structures for handling SDMX-JSON
messages related to GDS (Global Data Structure) metadata, such as
agency information.

Exports:
    JsonAgencyMessage: Represents the SDMX-JSON payload for agency queries.
"""

from pysdmx.io.json.gds.messages.org import (
    JsonAgencyMessage,
)
from pysdmx.io.json.gds.messages.services import (
    JsonServiceMessage,
)


__all__ = [
    "JsonAgencyMessage",
    "JsonServiceMessage",
]
