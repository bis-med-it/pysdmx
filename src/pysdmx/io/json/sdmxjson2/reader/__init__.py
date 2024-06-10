"""Collection of readers for SDMX-JSON messages."""

from pysdmx.api.fmr.reader import Deserializers
from pysdmx.io.json.sdmxjson2 import messages as msg

deserializers = Deserializers(
    agencies=msg.JsonAgencyMessage,  # type: ignore[arg-type]
    categories=msg.JsonCategorySchemeMessage,  # type: ignore[arg-type]
    codes=msg.JsonCodelistMessage,  # type: ignore[arg-type]
    concepts=msg.JsonConceptSchemeMessage,  # type: ignore[arg-type]
    dataflow=msg.JsonDataflowMessage,  # type: ignore[arg-type]
    providers=msg.JsonProviderMessage,  # type: ignore[arg-type]
    schema=msg.JsonSchemaMessage,  # type: ignore[arg-type]
    hier_assoc=msg.JsonHierarchyAssociationMessage,  # type: ignore[arg-type]
    hierarchy=msg.JsonHierarchyMessage,  # type: ignore[arg-type]
    report=msg.JsonMetadataMessage,  # type: ignore[arg-type]
    mapping=msg.JsonMappingMessage,  # type: ignore[arg-type]
    code_map=msg.JsonRepresentationMapMessage,  # type: ignore[arg-type]
)
