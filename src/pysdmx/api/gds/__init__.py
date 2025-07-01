"""API client for interacting with the GDS (Global Discovery Service) service.

This module provides classes and utilities to interact with the GDS service,
allowing retrieval of metadata such as agency information in SDMX-JSON format.

Exports: GdsClient: A synchronous client for retrieving metadata from
the GDS.
"""

from typing import Any, Literal, Optional, Sequence

from msgspec.json import decode

from pysdmx.api.qb.gds import GdsQuery, GdsType
from pysdmx.api.qb.service import GdsAsyncRestService, GdsRestService
from pysdmx.api.qb.util import REST_ALL
from pysdmx.io.json.gds.reader import deserializers as gds_readers
from pysdmx.io.serde import Deserializer
from pysdmx.model import Agency
from pysdmx.model.gds import (
    GdsCatalog,
    GdsSdmxApi,
    GdsService,
    GdsUrnResolver,
)

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
        return GdsQuery(artefact_type=GdsType.GDS_AGENCY, resource_id=agency)

    def _catalogs_q(
        self,
        agency: str,
        resource: str = REST_ALL,
        version: str = REST_ALL,
        resource_type: Optional[Literal["data", "metadata"]] = None,
        message_format: Optional[Literal["json", "csv", "xml"]] = None,
        api_version: Optional[str] = None,
        detail: Optional[Literal["full", "raw"]] = None,
        references: Optional[Literal["none", "children"]] = None,
    ) -> GdsQuery:
        return GdsQuery(
            artefact_type=GdsType.GDS_CATALOG,
            agency=agency,
            resource_id=resource,
            version=version,
            resource_type=resource_type,
            message_format=message_format,
            api_version=api_version,
            detail=detail,
            references=references,
        )

    def _sdmx_api_q(self, id: str = REST_ALL) -> GdsQuery:
        return GdsQuery(artefact_type=GdsType.GDS_SDMX_API, resource_id=id)

    def _services_q(
        self, agency: str, resource: str = REST_ALL, version: str = REST_ALL
    ) -> GdsQuery:
        return GdsQuery(
            artefact_type=GdsType.GDS_SERVICE,
            agency=agency,
            resource_id=resource,
            version=version,
        )

    def _urn_resolver_q(self, urn: str) -> GdsQuery:
        return GdsQuery(
            artefact_type=GdsType.GDS_URN_RESOLVER, resource_id=urn
        )


class GdsClient(__BaseGdsClient):
    """A client to be used to retrieve metadata from the GDS.

    With this client, metadata will be retrieved in a synchronous fashion.
    """

    def __init__(
        self,
        api_endpoint: str = GDS_BASE_ENDPOINT,
        pem: Optional[str] = None,
    ) -> None:
        """Instantiate a new client against the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            pem: In case the service exposed a certificate created
                by an unknown certificate authority, you can pass
                a pem file for this authority using this parameter.
        """
        super().__init__(api_endpoint, pem)
        self.__service = GdsRestService(
            self.api_endpoint,
            pem=pem,
            timeout=10.0,
        )

    def __fetch(
        self,
        query: GdsQuery,
    ) -> bytes:
        """Fetch the requested metadata from the GDS service."""
        return self.__service.gds(query)

    def get_agencies(self, agency: str) -> Sequence[Agency]:
        """Get the list of agencies for the supplied name.

        Args:
            agency: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        query = super()._agencies_q(agency)
        out = self.__fetch(query)
        agencies = super()._out(out, self.reader.agencies)
        return agencies

    def get_catalogs(
        self,
        catalog: str,
        resource: str = REST_ALL,
        version: str = REST_ALL,
        resource_type: Optional[Literal["data", "metadata"]] = None,
        message_format: Optional[Literal["json", "csv", "xml"]] = None,
        api_version: Optional[str] = None,
        detail: Optional[Literal["full", "raw"]] = None,
        references: Optional[Literal["none", "children"]] = None,
    ) -> Sequence[GdsCatalog]:
        """Get the list of catalogs for the supplied parameters.

        Args:
            catalog: The agency maintaining the catalog.
            resource: The resource ID(s) to query. Defaults to '*'.
            version: The version(s) of the resource. Defaults to '*'.
            resource_type: Filters the endpoints that support
             the requested resource type (eg, 'data', 'metadata')
            message_format: Filters the endpoints that support any
              of the requested message formats.
            api_version: Filters the endpoints that is in a
              specific SDMX API version.
              Multiple values separated by commas are possible.
              By default (if nothing is sent) it returns everything.
            detail: The amount of information to be returned.
              If detail=full: All available information for all artefacts
              should be returned.
              If detail=raw: Any nested service will be referenced.
            references: Instructs the web service to return
              (or not) the artefacts referenced by the
              artefact to be returned.
              If references=none: No referenced artefacts will be returned.
              If references=children: Returns the artefacts
              referenced by the artefact to be returned.

        Returns:
            A list of GdsCatalog objects.
        """
        query = super()._catalogs_q(
            catalog,
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

    def get_sdmx_apis(
        self, api_version: str = REST_ALL
    ) -> Sequence[GdsSdmxApi]:
        """Get the list of SDMX API versions.

        Args:
            api_version: The version of the SDMX API to be returned.
              Defaults to '*'.
        """
        query = super()._sdmx_api_q(api_version)
        response = self.__fetch(query)
        sdmx_api = super()._out(response, self.reader.sdmx_api)
        return sdmx_api

    def get_services(
        self, service: str, resource: str = REST_ALL, version: str = REST_ALL
    ) -> Sequence[GdsService]:
        """Get the list of services for the supplied parameters.

        Args:
            service: The agency maintaining the service.
            resource: The resource ID(s) to query. Defaults to '*'.
            version: The version(s) of the resource. Defaults to '*'.

        Returns:
            A list of GdsService objects.
        """
        query = super()._services_q(service, resource, version)
        response = self.__fetch(query)
        services = super()._out(response, self.reader.services)
        return services

    def get_urn_resolver(self, urn: str) -> GdsUrnResolver:
        """Resolve a URN to its corresponding resource.

        Args:
            urn: The URN to resolve.

        Returns:
            A GdsUrnResolver object with the resolved information.
        """
        query = super()._urn_resolver_q(urn)
        response = self.__fetch(query)
        urn_resolution = super()._out(response, self.reader.urn_resolver)
        return urn_resolution


class AsyncGdsClient(__BaseGdsClient):
    """A client to be used to retrieve metadata from the GDS asynchronously."""

    def __init__(
        self,
        api_endpoint: str = GDS_BASE_ENDPOINT,
        pem: Optional[str] = None,
    ) -> None:
        """Instantiate a new client against the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            pem: PEM file for unknown certificate authorities.
        """
        super().__init__(api_endpoint, pem)
        self.__service = GdsAsyncRestService(
            self.api_endpoint,
            pem=pem,
            timeout=10.0,
        )

    async def __fetch(self, query: GdsQuery) -> bytes:
        """Fetch the requested metadata from the GDS service asynchronously."""
        return await self.__service.gds(query)

    async def get_agencies(self, agency: str) -> Sequence[Agency]:
        """Get the list of agencies for the supplied name asynchronously.

        Args:
            agency: The agency maintaining the agency scheme.

        Returns:
            The requested list of agencies.
        """
        query = super(AsyncGdsClient, self)._agencies_q(agency)
        out = await self.__fetch(query)
        agencies = super(AsyncGdsClient, self)._out(out, self.reader.agencies)
        return agencies

    async def get_catalogs(
        self,
        catalog: str,
        resource: str = REST_ALL,
        version: str = REST_ALL,
        resource_type: Optional[Literal["data", "metadata"]] = None,
        message_format: Optional[Literal["json", "csv", "xml"]] = None,
        api_version: Optional[str] = None,
        detail: Optional[Literal["full", "raw"]] = None,
        references: Optional[Literal["none", "children"]] = None,
    ) -> Sequence[GdsCatalog]:
        """Get the list of catalogs for the supplied params asynchronously."""
        query = super()._catalogs_q(
            catalog,
            resource,
            version,
            resource_type,
            message_format,
            api_version,
            detail,
            references,
        )
        response = await self.__fetch(query)
        catalogs = super()._out(response, self.reader.catalogs)
        return catalogs

    async def get_sdmx_apis(
        self, api_version: str = REST_ALL
    ) -> Sequence[GdsSdmxApi]:
        """Get the list of SDMX API versions asynchronously."""
        query = super()._sdmx_api_q(api_version)
        response = await self.__fetch(query)
        sdmx_api = super()._out(response, self.reader.sdmx_api)
        return sdmx_api

    async def get_services(
        self, service: str, resource: str = REST_ALL, version: str = REST_ALL
    ) -> Sequence[GdsService]:
        """Get a list of services for the supplied params asynchronously."""
        query = super()._services_q(service, resource, version)
        response = await self.__fetch(query)
        services = super()._out(response, self.reader.services)
        return services

    async def get_urn_resolver(self, urn: str) -> GdsUrnResolver:
        """Resolve a URN to its corresponding resource asynchronously."""
        query = super()._urn_resolver_q(urn)
        response = await self.__fetch(query)
        urn_resolution = super()._out(response, self.reader.urn_resolver)
        return urn_resolution
