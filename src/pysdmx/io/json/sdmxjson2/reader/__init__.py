"""Collection of readers for SDMX-JSON messages."""

from pysdmx.io.json.sdmxjson2 import messages as msg
from pysdmx.io.serde import Deserializers


deserializers = Deserializers(
    agencies=msg.JsonAgencyMessage,  # type: ignore[arg-type]
    categories=msg.JsonCategorySchemeMessage,  # type: ignore[arg-type]
    codes=msg.JsonCodelistMessage,  # type: ignore[arg-type]
    concepts=msg.JsonConceptSchemeMessage,  # type: ignore[arg-type]
    dataflow_info=msg.JsonDataflowMessage,  # type: ignore[arg-type]
    dataflows=msg.JsonDataflowsMessage,  # type: ignore[arg-type]
    providers=msg.JsonProviderMessage,  # type: ignore[arg-type]
    schema=msg.JsonSchemaMessage,  # type: ignore[arg-type]
    hier_assoc=msg.JsonHierarchyAssociationMessage,  # type: ignore[arg-type]
    hierarchy=msg.JsonHierarchyMessage,  # type: ignore[arg-type]
    report=msg.JsonMetadataMessage,  # type: ignore[arg-type]
    mapping=msg.JsonMappingMessage,  # type: ignore[arg-type]
    code_map=msg.JsonRepresentationMapMessage,  # type: ignore[arg-type]
)
