from pysdmx.io.format import StructureFormat

from typing import Any, Optional

GDS_BASE_ENDPOINT = "https://gds.sdmx.io/"
ALLOWED_FORMATS = (
    StructureFormat.SDMX_JSON_2_0_0
)

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
                {"requested_format": fmt.value},
            )
        self.format = fmt
        if fmt == StructureFormat.FUSION_JSON:
            self.deser = fusion_readers
        else:
            self.deser = sdmx_readers

    def _out(self, response: bytes, typ: Deserializer, *params: Any) -> Any:
        return decode(response, type=typ).to_model(*params)