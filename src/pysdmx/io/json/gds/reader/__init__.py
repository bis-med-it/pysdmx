"""Collection of readers for SDMX-JSON messages."""

from pysdmx.io.json.gds import messages as msg
from pysdmx.io.serde import GdsDeserializers

deserializers = GdsDeserializers(
    agencies=msg.JsonAgencyMessage,
    catalogs=msg.JsonCatalogMessage,
    sdmx_api=msg.JsonSdmxApiMessage,
    services=msg.JsonServiceMessage,
    urn_resolver=msg.JsonUrnResolverMessage,
)
