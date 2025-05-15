"""Models for GDS data.

This module defines classes for representing GDS-specific data,
such as agencies, in the SDMX data model.

Exports:
    GdsAgency: Represents a GDS agency with attributes
               like ID, name, URL, and description.
"""

from typing import List, Optional

from msgspec import Struct


class GdsBase(Struct, frozen=True):
    """Base class for all GDS models with a custom __str__ method."""

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        out = []
        for k in self.__annotations__:
            v = self.__getattribute__(k)
            if v:
                out.append(f"{k}={v}")
        return ", ".join(out)


class GdsEndpoint(GdsBase, frozen=True):
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


class GdsServiceReference(GdsBase, frozen=True):
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


class GdsAgency(GdsBase, frozen=True):
    """Represents a GDS agency.

    Attributes:
        agency_id: The ID of the agency.
        name: The name of the agency.
        url: The URL of the agency.
        description: An optional description of the agency.
    """

    agency_id: str
    name: str
    url: str
    description: str = ""


class GdsCatalog(GdsBase, frozen=True):
    """Represents a GDS catalog.

    Attributes:
        agency_id: The ID of the agency.
        id: The ID of the catalog.
        name: The name of the catalog.
        urn: The URN of the catalog.
        version: The version of the catalog.
        endpoints: List of GDS endpoints available at the catalog.
    """

    agency_id: str
    id: str
    version: str
    name: str
    urn: str
    endpoints: Optional[List[GdsEndpoint]] = None
    serviceRefs: Optional[List[GdsServiceReference]] = None


class GdsService(GdsBase, frozen=True):
    """Represents a GDS catalog.

    Attributes:
        agency_id: The ID of the agency.
        id: The ID of the service.
        name: The name of the service.
        urn: The URN of the service.
        version: The version of the service.
        base: The base URL of the service.
        endpoints: List of GDS endpoints available at the service.
        authentication: Optional authentication method for the service.
    """

    agency_id: str
    id: str
    name: str
    urn: str
    version: str
    base: str
    endpoints: List[GdsEndpoint]
    authentication: Optional[str] = None


class GdsSdmxApi(GdsBase, frozen=True):
    """Represents an SDMX API version.

    Attributes:
        release: The release version of the SDMX API.
        description: A description of the release.
    """

    release: str
    description: str


class ResolverResult(GdsBase, frozen=True):
    """Represents a single resolver result.

    Attributes:
        api_version: The API version of the resolver result.
        query: The query URL for the resource.
        query_response_status_code: The HTTP response code for the query.
    """

    api_version: str
    query: str
    query_response_status_code: int


class GdsUrnResolver(GdsBase, frozen=True):
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
