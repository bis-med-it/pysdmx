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


class GdsServiceReference(Struct, frozen=True):
    """Represents a GDS service reference.
    Attributes:
        id: The ID of the service reference.
        name: The name of the service reference.
        urn: The URN of the service reference.
        service: The service associated with the reference.
        description: An optional description of the service reference.
    """

    id: str
    name: str
    urn: str
    service: str
    description: Optional[str] = None


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


class GdsCatalog(Struct, frozen=True):
    """Represents a GDS catalog.

    Attributes:
        agencyID: The ID of the agency.
        id: The ID of the catalog.
        name: The name of the catalog.
        urn: The URN of the catalog.
        version: The version of the catalog.
        endpoints: List of GDS endpoints available at the catalog.
    """

    agencyID: str
    id: str
    version: str
    name: str
    urn: str
    endpoints: Optional[List[GdsEndpoint]] = None
    serviceRefs: Optional[List[GdsServiceReference]] = None


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


class GdsSdmxApi(Struct, frozen=True):
    """Represents an SDMX API version.

    Attributes:
        release: The release version of the SDMX API.
        description: A description of the release.
    """
    release: str
    description: str


class ResolverResult(Struct, frozen=True):
    """Represents a single resolver result.

    Attributes:
        api_version: The API version of the resolver result.
        query: The query URL for the resource.
        query_response_status_code: The HTTP response code for the query.
    """
    api_version: str
    query: str
    query_response_status_code: int


class GdsUrnResolver(Struct, frozen=True):
    """Represents the response for a URN resolver query.

    Attributes:
        agency_id: The agency maintaining the resource.
        resource_id: The ID of the resource.
        version: The version of the resource.
        sdmx_type: The type of SDMX resource.
        resolver_results: A list of resolver results.
    """
    agency_id: str
    resource_id: str
    version: str
    sdmx_type: str
    resolver_results: List[ResolverResult]
