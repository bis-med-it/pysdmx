"""API client for interacting with the GDS (Global Data Structure) service.

This module provides classes and utilities to interact with the GDS service,
allowing retrieval of metadata such as agency information in SDMX-JSON format.

Exports: RegistryClient: A synchronous client for retrieving metadata from
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
from pysdmx.errors import NotImplemented
from pysdmx.io.format import (
    GdsFormat,
    RefMetaFormat,
    SchemaFormat,
    StructureFormat,
)
from pysdmx.io.json.gds.reader import deserializers as gds_readers
from pysdmx.io.serde import Deserializer
from pysdmx.model.gds import GdsAgency, GdsService, GdsCatalog

API_VERSION = ApiVersion.V2_0_0

GDS_BASE_ENDPOINT = "https://gds.sdmx.io/"

ALLOWED_STR_FORMATS = [
    GdsFormat.SDMX_JSON_2_0_0
]
READERS = {
    GdsFormat.SDMX_JSON_2_0_0: gds_readers,
}
RFM_FORMATS = {
    GdsFormat.SDMX_JSON_2_0_0: RefMetaFormat.SDMX_JSON_2_0_0
}
SCH_FORMATS = {
    GdsFormat.SDMX_JSON_2_0_0: SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE
}


class __BaseGdsClient:
    def __init__(
        self,
        api_endpoint: str = GDS_BASE_ENDPOINT,
        fmt: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        pem: Optional[str] = None,
    ):
        """Instantiate a new client against the target endpoint."""
        if api_endpoint.endswith("/"):
            api_endpoint = api_endpoint[0:-1]
        self.api_endpoint = api_endpoint
        if fmt not in ALLOWED_STR_FORMATS:
            raise NotImplemented(
                "Unsupported format",
                f"only {', '.join([f.value for f in ALLOWED_STR_FORMATS])}"
                          f" are supported",
                {"requested_format": fmt.value},
            )
        self.format = fmt
        self.reader = READERS[fmt]

    def _out(self, response: bytes, typ: Deserializer, *params: Any) -> Any:
        return decode(response, type=typ).to_model(*params)

    def _agencies_q(self, agency: str) -> GdsQuery:
        return GdsQuery(artefact_type=GdsType.GDS_AGENCY, agency_id=agency)

    def _catalogs_q(self,
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

    def _services_q(self, agency: str, resource: str = REST_ALL, version: str = REST_ALL) -> GdsQuery:
        return GdsQuery(
            artefact_type=GdsType.GDS_SERVICE,
            agency_id=agency,
            resource_id=resource,
            version=version
        )

    def _sdmx_api_q(self, id: str = REST_ALL) -> GdsQuery:
        return GdsQuery(
            artefact_type=GdsType.GDS_SDMX_API,
            agency_id=id
        )


class GdsClient(__BaseGdsClient):
    """A client to be used to retrieve metadata from the GDS.

    With this client, metadata will be retrieved in a synchronous fashion.
    """

    def __init__(
        self,
            api_endpoint: str,
            format: GdsFormat = GdsFormat.SDMX_JSON_2_0_0,
            pem: Optional[str] = None,
    ) -> None:
        """Instantiate a new client against the target endpoint.

        Args:
            api_endpoint: The endpoint of the targeted service.
            format: The format the service should use to serialize
                the metadata to be returned. Defaults to SDMX-JSON.
            pem: In case the service exposed a certificate created
                by an unknown certificate authority, you can pass
                a pem file for this authority using this parameter.
        """
        super().__init__(api_endpoint, format, pem)
        self.__service = RestService(
            self.api_endpoint,
            API_VERSION,
            gds_format=format,
            pem=pem,
            timeout=10.0,
        )

    def __fetch(
        self,
        query: GdsQuery,
    ) -> bytes:
        """Fetch the requested metadata from the GDS service."""
        return self.__service.gds(query)

    def get_agencies(self, agency: str) -> Sequence[GdsAgency]:
        """Get the list of **sub-agencies** for the supplied agency.

        Args:
            agency: The agency maintaining the agency scheme from
                which sub-agencies must be returned.

        Returns:
            The requested list of agencies.
        """
        query = super()._agencies_q(agency)
        out = self.__fetch(query)
        schemes = super()._out(out, self.reader.agencies)
        return schemes

    def get_catalogs(
            self,
            agency: str,
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
            agency: The agency maintaining the catalog.
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
            agency,
            resource,
            version,
            resource_type,
            message_format,
            api_version,
            detail,
            references
        )
        response = self.__fetch(query)
        catalogs = super()._out(response, self.reader.catalogs)
        return catalogs

    def get_services(self, agency: str, resource: str = REST_ALL, version: str = REST_ALL) -> Sequence[GdsService]:
        """Get the list of services for the supplied parameters.

        Args:
            agency: The agency maintaining the service.
            resource: The resource ID(s) to query. Defaults to '*'.
            version: The version(s) to query. Defaults to '*'.

        Returns:
            A list of GdsService objects.
        """
        query = super()._services_q(agency, resource, version)
        response = self.__fetch(query)
        schemes = super()._out(response, self.reader.services)
        return schemes


    def get_sdmx_api(self, id: str = REST_ALL):
        query = super()._sdmx_api_q(id)
        response = self.__fetch(query)
        sdmx_apis = super()._out(response, self.reader.sdmxapi)
        return sdmx_apis
