"""Module for GDS-JSON GDS message schemas.

This module provides classes and structures for handling GDS-JSON
messages related to GDS (Global Discovery Service) metadata, such as
agency information.

Exports:
    JsonAgencyMessage: Represents the GDS-JSON payload for agency queries.
"""

from pysdmx.io.json.gds.messages.agencies import (
    JsonAgencyMessage,
)
from pysdmx.io.json.gds.messages.catalog import (
    JsonCatalogMessage,
)
from pysdmx.io.json.gds.messages.sdmx_api import (
    JsonSdmxApiMessage,
)
from pysdmx.io.json.gds.messages.services import (
    JsonServiceMessage,
)
from pysdmx.io.json.gds.messages.urn_resolver import (
    JsonUrnResolverMessage,
    JsonUrnResolverResult,
)

__all__ = [
    "JsonAgencyMessage",
    "JsonCatalogMessage",
    "JsonSdmxApiMessage",
    "JsonServiceMessage",
    "JsonUrnResolverMessage",
    "JsonUrnResolverResult",
]
