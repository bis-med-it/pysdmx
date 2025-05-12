from typing import Any, Optional, Sequence

from msgspec.json import decode

from pysdmx.api.qb import (
    ApiVersion,
    RestService,
)
from pysdmx.api.qb.gds import GdsQuery, GdsType
from pysdmx.errors import NotImplemented
from pysdmx.io.format import (
    GdsFormat,
    RefMetaFormat,
    SchemaFormat,
    StructureFormat,
)
from pysdmx.io.json.gds.reader import deserializers as gds_readers
from pysdmx.io.serde import Deserializer
from pysdmx.model.gds import GdsAgency

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

    def _agencies_q(self, agency: str) -> GdsQuery:
        return GdsQuery(artefact_type=GdsType.GDS_AGENCY, agency_id=agency)


class RegistryClient(__BaseRegistryClient):
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
            structure_format=format,
            schema_format=SCH_FORMATS[format],
            refmeta_format=RFM_FORMATS[format],
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
