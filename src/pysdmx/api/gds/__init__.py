"""API client for interacting with the GDS (Global Discovery Service) service.

This module provides classes and utilities to interact with the GDS service,
allowing retrieval of metadata such as agency information in SDMX-JSON format.

Exports: GdsClient: A synchronous client for retrieving metadata from
the GDS.
"""

from typing import Any, Optional, Sequence

from msgspec.json import decode

from pysdmx.api.qb import (
    ApiVersion,
    RestService,
)
from pysdmx.api.qb.gds import GdsQuery, GdsType
from pysdmx.api.qb.util import REST_ALL
from pysdmx.io.json.gds.reader import deserializers as gds_readers
from pysdmx.io.serde import Deserializer
from pysdmx.model.gds import (
    GdsAgency,
    GdsCatalog,
    GdsSdmxApi,
    GdsService,
    GdsUrnResolver,
)

API_VERSION = ApiVersion.V2_0_0

GDS_BASE_ENDPOINT = "https://gds.sdmx.io/"

READERS = gds_readers


class __BaseGdsClient:
    def __init__(
        self,
        api_endpoint: str = GDS_BASE_ENDPOINT,
        pem: Optional[str] = None,
    ):
        """Instantiate a new client against the target endpoint."""
        if api_endpoint.endswith("/"):
            api_endpoint = api_endpoint[0:-1]
        self.api_endpoint = api_endpoint
        self.reader = READERS

    def _out(self, response: bytes, typ: Deserializer, *params: Any) -> Any:
        return decode(response, type=typ).to_model(*params)

    def _agencies_q(self, agency: str) -> GdsQuery:
        return GdsQuery(artefact_type=GdsType.GDS_AGENCY, agency_id=agency)

    def _catalogs_q(
        self,
        agency: str,
        resource: str = REST_ALL,
        version: str = REST_ALL,
        resource_type: Optional[str] = None,
        message_format: Optional[str] = None,
        api_version: Optional[str] = None,
        detail: Optional[str] = None,
        references: Optional[str] = None,
    ) -> GdsQuery:
        return GdsQuery(
            artefact_type=GdsType.GDS_CATALOG,
            agency_id=agency,
            resource_id=resource,
            version=version,
            resource_type=resource_type,
            message_format=message_format,
            api_version=api_version,
            detail=detail,
            references=references,
        )

    def _sdmx_api_q(self, id: str = REST_ALL) -> GdsQuery:
        return GdsQuery(artefact_type=GdsType.GDS_SDMX_API, agency_id=id)

    def _services_q(
        self, agency: str, resource: str = REST_ALL, version: str = REST_ALL
    ) -> GdsQuery:
        return GdsQuery(
            artefact_type=GdsType.GDS_SERVICE,
            agency_id=agency,
            resource_id=resource,
            version=version,
        )

    def _urn_resolver_q(self, urn: str) -> GdsQuery:
        return GdsQuery(artefact_type=GdsType.GDS_URN_RESOLVER, agency_id=urn)


class GdsClient(__BaseGdsClient):
    """A client to be used to retrieve metadata from the GDS.

    With this client, metadata will be retrieved in a synchronous fashion.
    """

    def __init__(
        self,
        api_endpoint: str = GDS_BASE_ENDPOINT,
        api_version: ApiVersion = API_VERSION,
        pem: Optional[str] = None,
    ) -> None:
        """Instantiate a new client against the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            api_version: version of the api to execute the query.
            pem: In case the service exposed a certificate created
                by an unknown certificate authority, you can pass
                a pem file for this authority using this parameter.
        """
        super().__init__(api_endpoint, pem)
        self.__service = RestService(
            self.api_endpoint,
            api_version=api_version,
            pem=pem,
            timeout=10.0,
        )

    def __fetch(
        self,
        query: GdsQuery,
    ) -> bytes:
        """Fetch the requested metadata from the GDS service."""
        return self.__service.gds(query)

    def get_agencies(self, ref: str) -> Sequence[GdsAgency]:
        """Get the list of agencies for the supplied name.

        Args:
            ref: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        query = super()._agencies_q(ref)
        out = self.__fetch(query)
        schemes = super()._out(out, self.reader.agencies)
        return schemes

    def get_catalogs(
        self,
        ref: str,
        resource: str = REST_ALL,
        version: str = REST_ALL,
        resource_type: Optional[str] = None,
        message_format: Optional[str] = None,
        api_version: Optional[str] = None,
        detail: Optional[str] = None,
        references: Optional[str] = None,
    ) -> Sequence[GdsCatalog]:
        """Get the list of catalogs for the supplied parameters.

        Args:
            ref: The agency maintaining the catalog.
            resource: The resource ID(s) to query. Defaults to '*'.
            version: The version(s) to query. Defaults to '*'.
            resource_type: The type of resource (e.g., 'data', 'metadata').
            message_format: The message format(s) (e.g., 'json', 'csv').
            api_version: The API version(s) (e.g., '2.0.0').
            detail: The level of detail ('full', 'raw').
            references: The references to include ('none', 'children').

        Returns:
            A list of GdsCatalog objects.
        """
        query = super()._catalogs_q(
            ref,
            resource,
            version,
            resource_type,
            message_format,
            api_version,
            detail,
            references,
        )
        response = self.__fetch(query)
        catalogs = super()._out(response, self.reader.catalogs)
        return catalogs

    def get_sdmx_api(self, ref: str = REST_ALL) -> Sequence[GdsSdmxApi]:
        """Get the list of SDMX API versions.

        Args:
            ref: The ID of the SDMX API version to query. Defaults to '*'.
        """
        query = super()._sdmx_api_q(ref)
        response = self.__fetch(query)
        sdmx_apis = super()._out(response, self.reader.sdmx_api)
        return sdmx_apis

    def get_services(
        self, ref: str, resource: str = REST_ALL, version: str = REST_ALL
    ) -> Sequence[GdsService]:
        """Get the list of services for the supplied parameters.

        Args:
            ref: The agency maintaining the service.
            resource: The resource ID(s) to query. Defaults to '*'.
            version: The version(s) to query. Defaults to '*'.

        Returns:
            A list of GdsService objects.
        """
        query = super()._services_q(ref, resource, version)
        response = self.__fetch(query)
        schemes = super()._out(response, self.reader.services)
        return schemes

    def get_urn_resolver(self, ref: str) -> GdsUrnResolver:
        """Resolve a URN to its corresponding resource.

        Args:
            ref: The URN to resolve.

        Returns:
            A GdsUrnResolver object with the resolved information.
        """
        query = super()._urn_resolver_q(ref)
        response = self.__fetch(query)
        urn_resolver = super()._out(response, self.reader.urn_resolver)
        return urn_resolver
