"""Models for GDS data.

This module defines classes for representing GDS-specific data,
such as agencies, in the SDMX data model.

Exports:
    GdsAgency: Represents a GDS agency with attributes
               like ID, name, URL, and description.
"""

from typing import Optional, List

from msgspec import Struct

from pysdmx.model import Agency


class GdsAgency(Struct, frozen=True):
    """Represents a GDS agency.

    Attributes:
        agencyId: The ID of the agency.
        name: The name of the agency.
        url: The URL of the agency.
        description: An optional description of the agency.
    """

    agencyId: str
    name: str
    url: str
    description: str = ""

    def to_model(self, owner: Optional[str] = None) -> Agency:
        """Converts a GdsOrg to a standard Organisation."""
        d = self.description
        oid = f"{owner}.{self.agencyId}" if (owner and
                 owner != "SDMX") else self.agencyId
        return Agency(id=oid, name=self.name, description=d, contacts=None)


class GdsEndpoint(Struct, frozen=True):
    """Represents a GDS endpoint.

    Attributes:
        api_version: The API version of the endpoint.
        url: The URL of the endpoint.
        comments: Comments about the endpoint.
        message_formats: List of message formats supported by the endpoint.
        rest_resources: List of REST resources available at the endpoint.
    """
    api_version: str
    url: str
    comments: str
    message_formats: List[str]
    rest_resources: List[str]


class GdsService(Struct, frozen=True):
    """Represents a GDS catalog.

    Attributes:
        agencyID: The ID of the agency.
        id: The ID of the service.
        name: The name of the service.
        urn: The URN of the service.
        version: The version of the service.
        base: The base URL of the service.
        endpoints: List of GDS endpoints available at the service.
        authentication: Optional authentication method for the service.
    """

    agencyID: str
    id: str
    name: str
    urn: str
    version: str
    base: str
    endpoints: List[GdsEndpoint]
    authentication: Optional[str] = None
