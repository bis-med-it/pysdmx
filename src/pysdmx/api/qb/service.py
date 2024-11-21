"""Connector to SDMX-REST services."""

from typing import NoReturn, Optional, Union

import httpx

from pysdmx import errors
from pysdmx.api.qb.availability import AvailabilityFormat, AvailabilityQuery
from pysdmx.api.qb.data import DataFormat, DataQuery
from pysdmx.api.qb.refmeta import (
    RefMetaByMetadataflowQuery,
    RefMetaByMetadatasetQuery,
    RefMetaByStructureQuery,
    RefMetaFormat,
)
from pysdmx.api.qb.schema import SchemaFormat, SchemaQuery
from pysdmx.api.qb.structure import StructureFormat, StructureQuery
from pysdmx.api.qb.util import ApiVersion


class RestService:
    """Connector to SDMX-REST services."""

    def __init__(
        self,
        api_endpoint: str,
        api_version: ApiVersion,
        data_format: DataFormat = DataFormat.SDMX_JSON_2_0_0,
        structure_format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        schema_format: SchemaFormat = SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE,
        refmeta_format: RefMetaFormat = RefMetaFormat.SDMX_JSON_2_0_0,
        avail_format: AvailabilityFormat = AvailabilityFormat.SDMX_JSON_2_0_0,
        pem: Optional[str] = None,
    ):
        """Instantiate a connector to a SDMX-REST service."""
        self.__api_endpoint = (
            api_endpoint[0:-1] if api_endpoint.endswith("/") else api_endpoint
        )

        self.__api_version = api_version
        self.__data_format = data_format
        self.__structure_format = structure_format
        self.__schema_format = schema_format
        self.__refmeta_format = refmeta_format
        self.__avail_format = avail_format
        self.__ssl_context = (
            httpx.create_ssl_context(
                verify=pem,
            )
            if pem
            else httpx.create_ssl_context()
        )
        self.headers = {
            "Accept-Encoding": "gzip, deflate",
        }

    def data(self, query: DataQuery) -> bytes:
        """Execute a data query against the service."""
        q = query.get_url(self.__api_version, True)
        f = self.__data_format.value
        return self.__fetch(q, f)

    def structure(self, query: StructureQuery) -> bytes:
        """Execute a structure query against the service."""
        q = query.get_url(self.__api_version, True)
        f = self.__structure_format.value
        return self.__fetch(q, f)

    def schema(self, query: SchemaQuery) -> bytes:
        """Execute a schema query against the service."""
        q = query.get_url(self.__api_version, True)
        f = self.__schema_format.value
        return self.__fetch(q, f)

    def availability(self, query: AvailabilityQuery) -> bytes:
        """Execute an availability query against the service."""
        q = query.get_url(self.__api_version, True)
        f = self.__avail_format.value
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
        q = query.get_url(self.__api_version, True)
        f = self.__refmeta_format.value
        return self.__fetch(q, f)

    def __fetch(self, query: str, format: str) -> bytes:
        with httpx.Client(verify=self.__ssl_context) as client:
            try:
                url = f"{self.__api_endpoint}{query}"
                h = self.headers.copy()
                h["Accept"] = format
                r = client.get(url, headers=h)
                r.raise_for_status()
                return r.content
            except (httpx.RequestError, httpx.HTTPStatusError) as e:
                self.__map_error(e)

    def __map_error(
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
