from msgspec.json import decode

from pysdmx.api.qb import (
    ApiVersion,
    RestService,
)
from pysdmx.io.format import RefMetaFormat, SchemaFormat, StructureFormat
from pysdmx.io.json.sdmxjson2.reader import deserializers as sdmx2_readers
from pysdmx.io.serde import Deserializer
from pysdmx.errors import NotImplemented

from typing import Any, Optional


API_VERSION = ApiVersion.V2_0_0

GDS_BASE_ENDPOINT = "https://gds.sdmx.io/"

ALLOWED_STR_FORMATS = (
    StructureFormat.SDMX_JSON_2_0_0
)
READERS = {
    StructureFormat.SDMX_JSON_2_0_0: sdmx2_readers,
}
RFM_FORMATS = {
    StructureFormat.SDMX_JSON_2_0_0: RefMetaFormat.SDMX_JSON_2_0_0
}
SCH_FORMATS = {
    StructureFormat.SDMX_JSON_2_0_0: SchemaFormat.SDMX_JSON_2_0_0_STRUCTURE
}


class __BaseRegistryClient:
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
                f"only {', '.join([f.value for f in ALLOWED_STR_FORMATS])} are supported",
                {"requested_format": fmt.value},
            )
        self.format = fmt
        self.reader = READERS[fmt]

    def _out(self, response: bytes, typ: Deserializer, *params: Any) -> Any:
        return decode(response, type=typ).to_model(*params)


class RegistryClient(__BaseRegistryClient):
    """A client to be used to retrieve metadata from the GDS.

    With this client, metadata will be retrieved in a synchronous fashion.
    """

    def __init__(
        self,
        api_endpoint: str,
        format: StructureFormat = StructureFormat.SDMX_JSON_2_0_0,
        pem: Optional[str] = None,
    ):
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
            structure_format=format,
            schema_format=SCH_FORMATS[format],
            refmeta_format=RFM_FORMATS[format],
            pem=pem,
            timeout=10.0,
        )
