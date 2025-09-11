"""Collection of writers for SDMX-JSON messages."""

from pysdmx.io.json.sdmxjson2 import messages as msg
from pysdmx.io.serde import Serializers

serializers = Serializers(
    metadata_message=msg.JsonMetadataMessage,
    structure_message=msg.JsonStructureMessage,
)
