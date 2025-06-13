"""Connector to SDMX-REST and GDS-REST services."""

from typing import NoReturn, Optional, Union

import httpx

from pysdmx import errors
from pysdmx.api.qb.availability import AvailabilityFormat, AvailabilityQuery
from pysdmx.api.qb.data import DataFormat, DataQuery
from pysdmx.api.qb.gds import GdsQuery
from pysdmx.api.qb.refmeta import (
    RefMetaByMetadataflowQuery,
    RefMetaByMetadatasetQuery,
    RefMetaByStructureQuery,
    RefMetaFormat,
)
from pysdmx.api.qb.registration import (
    RegistrationByContextQuery,
    RegistrationByIdQuery,
    RegistrationByProviderQuery,
    RegistryFormat,
)
from pysdmx.api.qb.schema import SchemaFormat, SchemaQuery
from pysdmx.api.qb.structure import StructureFormat, StructureQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.io.format import GDS_FORMAT


class _CoreRestService:
    """Abstract connector."""

    def __init__(
        self,
        api_endpoint: str,
        api_version: ApiVersion,
        data_format: DataFormat,
        structure_format: StructureFormat,
        schema_format: SchemaFormat,
        refmeta_format: RefMetaFormat,
        avail_format: AvailabilityFormat,
        registry_format: RegistryFormat,
        pem: Optional[str] = None,
        timeout: Optional[float] = 5.0,
    ):
        """Instantiate a connector to a SDMX-REST service."""
        self._api_endpoint = (
            api_endpoint[0:-1] if api_endpoint.endswith("/") else api_endpoint
        )

        self._api_version = api_version
        self._data_format = data_format
        self._structure_format = structure_format
        self._schema_format = schema_format
        self._refmeta_format = refmeta_format
        self._avail_format = avail_format
        self._registry_format = registry_format
        self._ssl_context = (
            httpx.create_ssl_context(
                verify=pem,
            )
            if pem
            else httpx.create_ssl_context()
        )
        self._headers = {
            "Accept-Encoding": "gzip, deflate",
        }
        self._timeout = timeout

    def _map_error(
        self, e: Union[httpx.RequestError, httpx.HTTPStatusError]
    ) -> NoReturn:
        q = e.request.url
        if isinstance(e, httpx.HTTPStatusError):
            s = e.response.status_code
            t = e.response.text
            if s == 404:
                msg = (
                    "The requested resource(s) could not be found in the "
                    f"targeted service. The query was `{q}`"
                )
                raise errors.NotFound("Not found", msg) from e
            elif s < 500:
                msg = (
                    f"The query returned a {s} error code. The query "
                    f"was `{q}`. The error message was: `{t}`."
                )
                raise errors.Invalid(f"Client error {s}", msg) from e
            else:
                msg = (
                    f"The service returned a {s} error code. The query "
                    f"was `{q}`. The error message was: `{t}`."
                )
                raise errors.InternalError(f"Service error {s}", msg) from e
        else:
            msg = (
                f"There was an issue connecting to the targeted service. "
                f"The query was `{q}`. The error message was: `{e}`."
            )
            raise errors.Unavailable("Connection error", msg) from e


class RestService(_CoreRestService):
    """Synchronous connector to SDMX-REST services.

    Args:
        api_endpoint: The entry point (URL) of the SDMX-REST service.
        api_version: The most recent version of the SDMX-REST specification
            supported by the service.
        data_format: The default format for data queries.
        structure_format: The default format for structure queries.
        schema_format: The default format for schema queries.
        refmeta_format: The default format for reference metadata queries.
        avail_format: The default format for availability queries.
        registry_format: The default format for registration queries.
        pem: In case the service uses SSL/TLS with self-signed certificate,
            this attribute should be used to pass the pem file with the
            list of trusted certicate authorities.
        timeout: The maximum number of seconds to wait before considering
            that a request timed out. Defaults to 5 seconds.
    """

    def __init__(
        self,
        api_endpoint: str,
        api_version: ApiVersion,
        data_format: DataFormat = DataFormat.SDMX_JSON_2_0_0,
        structure_format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        schema_format: SchemaFormat = SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE,
        refmeta_format: RefMetaFormat = RefMetaFormat.SDMX_JSON_2_0_0,
        avail_format: AvailabilityFormat = AvailabilityFormat.SDMX_JSON_2_0_0,
        registry_format: RegistryFormat = RegistryFormat.FUSION_JSON,
        pem: Optional[str] = None,
        timeout: Optional[float] = 5.0,
    ):
        """Instantiate a connector to a SDMX-REST service."""
        super().__init__(
            api_endpoint,
            api_version,
            data_format,
            structure_format,
            schema_format,
            refmeta_format,
            avail_format,
            registry_format,
            pem,
            timeout,
        )

    def data(self, query: DataQuery) -> bytes:
        """Execute a data query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._data_format.value
        return self.__fetch(q, f)

    def structure(self, query: StructureQuery) -> bytes:
        """Execute a structure query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._structure_format.value
        return self.__fetch(q, f)

    def schema(self, query: SchemaQuery) -> bytes:
        """Execute a schema query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._schema_format.value
        return self.__fetch(q, f)

    def availability(self, query: AvailabilityQuery) -> bytes:
        """Execute an availability query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._avail_format.value
        return self.__fetch(q, f)

    def reference_metadata(
        self,
        query: Union[
            RefMetaByMetadataflowQuery,
            RefMetaByMetadatasetQuery,
            RefMetaByStructureQuery,
        ],
    ) -> bytes:
        """Execute a reference metadata query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._refmeta_format.value
        return self.__fetch(q, f)

    def registration(
        self,
        query: Union[
            RegistrationByContextQuery,
            RegistrationByIdQuery,
            RegistrationByProviderQuery,
        ],
    ) -> bytes:
        """Execute a registration query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._registry_format.value
        return self.__fetch(q, f)

    def __fetch(self, query: str, format: str) -> bytes:
        with httpx.Client(verify=self._ssl_context) as client:
            try:
                url = f"{self._api_endpoint}{query}"
                h = self._headers.copy()
                h["Accept"] = format
                r = client.get(url, headers=h, timeout=self._timeout)
                r.raise_for_status()
                return r.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._map_error(e)


class AsyncRestService(_CoreRestService):
    """Asynchronous connector to SDMX-REST services.

    Args:
        api_endpoint: The entry point (URL) of the SDMX-REST service.
        api_version: The most recent version of the SDMX-REST specification
            supported by the service.
        data_format: The default format for data queries.
        structure_format: The default format for structure queries.
        schema_format: The default format for schema queries.
        refmeta_format: The default format for reference metadata queries.
        avail_format: The default format for availability queries.
        registry_format: The default format for registration queries.
        pem: In case the service uses SSL/TLS with self-signed certificate,
            this attribute should be used to pass the pem file with the
            list of trusted certicate authorities.
        timeout: The maximum number of seconds to wait before considering
            that a request timed out. Defaults to 5 seconds.
    """

    def __init__(
        self,
        api_endpoint: str,
        api_version: ApiVersion,
        data_format: DataFormat = DataFormat.SDMX_JSON_2_0_0,
        structure_format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        schema_format: SchemaFormat = SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE,
        refmeta_format: RefMetaFormat = RefMetaFormat.SDMX_JSON_2_0_0,
        avail_format: AvailabilityFormat = AvailabilityFormat.SDMX_JSON_2_0_0,
        registry_format: RegistryFormat = RegistryFormat.FUSION_JSON,
        pem: Optional[str] = None,
        timeout: Optional[float] = 5.0,
    ):
        """Instantiate a connector to a SDMX-REST service."""
        super().__init__(
            api_endpoint,
            api_version,
            data_format,
            structure_format,
            schema_format,
            refmeta_format,
            avail_format,
            registry_format,
            pem,
            timeout,
        )

    async def data(self, query: DataQuery) -> bytes:
        """Execute a data query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._data_format.value
        out = await self.__fetch(q, f)
        return out

    async def structure(self, query: StructureQuery) -> bytes:
        """Execute a structure query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._structure_format.value
        out = await self.__fetch(q, f)
        return out

    async def schema(self, query: SchemaQuery) -> bytes:
        """Execute a schema query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._schema_format.value
        out = await self.__fetch(q, f)
        return out

    async def availability(self, query: AvailabilityQuery) -> bytes:
        """Execute an availability query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._avail_format.value
        out = await self.__fetch(q, f)
        return out

    async def reference_metadata(
        self,
        query: Union[
            RefMetaByMetadataflowQuery,
            RefMetaByMetadatasetQuery,
            RefMetaByStructureQuery,
        ],
    ) -> bytes:
        """Execute a reference metadata query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._refmeta_format.value
        out = await self.__fetch(q, f)
        return out

    async def registration(
        self,
        query: Union[
            RegistrationByContextQuery,
            RegistrationByIdQuery,
            RegistrationByProviderQuery,
        ],
    ) -> bytes:
        """Execute a registration query against the service."""
        q = query.get_url(self._api_version, True)
        f = self._registry_format.value
        out = await self.__fetch(q, f)
        return out

    async def __fetch(self, query: str, format: str) -> bytes:
        async with httpx.AsyncClient(verify=self._ssl_context) as client:
            try:
                url = f"{self._api_endpoint}{query}"
                h = self._headers.copy()
                h["Accept"] = format
                r = await client.get(url, headers=h, timeout=self._timeout)
                r.raise_for_status()
                return r.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._map_error(e)


class _CoreGdsRestService:
    """Base class for GDS-REST services."""

    def __init__(
        self,
        api_endpoint: str,
        pem: Optional[str] = None,
        timeout: float = 5.0,
    ):
        self._api_endpoint = api_endpoint.rstrip("/")
        self._ssl_context = (
            httpx.create_ssl_context(verify=pem)
            if pem
            else httpx.create_ssl_context()
        )
        self._headers = {"Accept-Encoding": "gzip, deflate"}
        self._timeout = timeout

    def _map_error(
        self, e: Union[httpx.RequestError, httpx.HTTPStatusError]
    ) -> NoReturn:
        q = e.request.url
        if isinstance(e, httpx.HTTPStatusError):
            s = e.response.status_code
            t = e.response.text
            if s == 404:
                msg = (
                    f"The requested resource(s) could "
                    f"not be found. Query: `{q}`"
                )
                raise errors.NotFound("Not found", msg) from e
            elif s < 500:
                msg = f"Client error {s}. Query: `{q}`. Error: `{t}`."
                raise errors.Invalid(f"Client error {s}", msg) from e
            else:
                msg = f"Service error {s}. Query: `{q}`. Error: `{t}`."
                raise errors.InternalError(f"Service error {s}", msg) from e
        else:
            msg = f"Connection error. Query: `{q}`. Error: `{e}`."
            raise errors.Unavailable("Connection error", msg) from e


class GdsRestService(_CoreGdsRestService):
    """Synchronous GDS-REST service."""

    def _fetch(self, query: str, format_: str) -> bytes:
        with httpx.Client(verify=self._ssl_context) as client:
            try:
                url = f"{self._api_endpoint}{query}"
                headers = {**self._headers, "Accept": format_}
                response = client.get(
                    url, headers=headers, timeout=self._timeout
                )
                response.raise_for_status()
                return response.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._map_error(e)

    def gds(self, query: GdsQuery) -> bytes:
        """Execute a GDS query against the service."""
        q = query.get_url()
        return self._fetch(q, GDS_FORMAT)


class GdsAsyncRestService(_CoreGdsRestService):
    """Asynchronous GDS-REST service."""

    async def _fetch(self, query: str, format_: str) -> bytes:
        async with httpx.AsyncClient(verify=self._ssl_context) as client:
            try:
                url = f"{self._api_endpoint}{query}"
                headers = {**self._headers, "Accept": format_}
                response = await client.get(
                    url, headers=headers, timeout=self._timeout
                )
                response.raise_for_status()
                return response.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self._map_error(e)

    async def gds(self, query: GdsQuery) -> bytes:
        """Execute a GDS query against the service."""
        q = query.get_url()
        return await self._fetch(q, GDS_FORMAT)
