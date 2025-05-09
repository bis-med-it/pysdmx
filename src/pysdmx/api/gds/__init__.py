from msgspec.json import decode

from pysdmx.errors import NotImplemented
from pysdmx.io.format import StructureFormat
from pysdmx.io.json.sdmxjson2.reader import deserializers as sdmx_2_0_readers

from typing import Any, Optional


GDS_BASE_ENDPOINT = "https://gds.sdmx.io/"
ALLOWED_FORMATS = (
    StructureFormat.SDMX_JSON_2_0_0
)
READERS = {
    StructureFormat.SDMX_JSON_2_0_0: sdmx_2_0_readers,
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
        if fmt not in ALLOWED_FORMATS:
            raise NotImplemented(
                "Unsupported format",
                f"only {', '.join([f.value for f in ALLOWED_FORMATS])} are supported",
                {"requested_format": fmt.value},
            )
        self.format = fmt
        self.reader = READERS[fmt]

    def _out(self, response: bytes, typ: Deserializer, *params: Any) -> Any:
        return decode(response, type=typ).to_model(*params)