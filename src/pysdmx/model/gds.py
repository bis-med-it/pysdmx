"""Models for GDS data.

This module defines classes for representing GDS-specific data,
such as agencies, in the SDMX data model.
"""

from typing import List, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.model.__base import MaintainableArtefact
from pysdmx.util import parse_maintainable_urn


class GdsBase(Struct, repr_omit_defaults=True, frozen=True):
    """Base class for all GDS models with a custom __str__ method."""

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # str is taken as a Sequence, so we need to check it's not a str
            if isinstance(value, Sequence) and not isinstance(value, str):
                # Handle non-empty lists
                if not value:
                    continue
                class_name = value[0].__class__.__name__
                value = f"{len(value)} {class_name.lower()}s"

            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # Omit empty sequences
            if isinstance(value, (list, tuple, set)) and not value:
                continue
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


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

    @property
    def short_urn(self) -> str:
        """Returns a short URN for the ServiceReference."""
        return parse_maintainable_urn(self.service).__str__()


class GdsService(GdsBase, MaintainableArtefact, frozen=True, kw_only=True):
    """Represents a GDS service.

    Attributes:
        agency: The AgencyID of the service's owner.
        base: The base URL of the service.
        endpoints: List of GDS endpoints available at the service.
        authentication: Optional authentication method for the service.
    """

    base: str
    endpoints: List[GdsEndpoint]
    authentication: Optional[str] = None


class GdsCatalog(GdsBase, MaintainableArtefact, frozen=True, kw_only=True):
    """Represents a GDS catalog.

    Attributes:
        agency: The AgencyID of the catalog's owner.
        id: The ID of the catalog.
        urn: The URN of the catalog.
        version: The version of the catalog.
        services: Optional list of GdsService or GdsServiceReference,
        depending on the references parameter, that are associated with the
        catalog.
        endpoints: List of GDS endpoints available at the catalog.
    """

    services: Optional[List[Union[GdsService, GdsServiceReference]]] = None
    endpoints: Optional[List[GdsEndpoint]] = None


class GdsSdmxApi(GdsBase, frozen=True):
    """Represents an SDMX API version.

    Attributes:
        release: The release version of the SDMX API.
        description: A description of the release.
    """

    release: str
    description: str


class ResolverResult(
    GdsBase, frozen=True, rename={"query_response_status_code": "status_code"}
):
    """Represents a single resolver result.

    Attributes:
        api_version: The API version of the resolver result.
        query: The query URL for the resource.
        status_code: The HTTP response code for the query.
    """

    api_version: str
    query: str
    status_code: int


class GdsUrnResolver(GdsBase, frozen=True):
    """Represents the response for a URN resolver query.

    Attributes:
        agency: The agency maintaining the resource.
        resource_id: The ID of the resource.
        version: The version of the resource.
        sdmx_type: The type of SDMX resource.
        resolver_results: A list of resolver results.
    """

    agency: str
    resource_id: str
    version: str
    sdmx_type: str
    resolver_results: List[ResolverResult]
