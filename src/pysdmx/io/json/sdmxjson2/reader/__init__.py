"""Collection of readers for SDMX-JSON messages."""

from pysdmx.fmr.reader import Deserializers
from pysdmx.io.json.sdmxjson2.messages.category import (
    JsonCategorySchemeMessage,
)
from pysdmx.io.json.sdmxjson2.messages.code import (
    JsonCodelistMessage,
    JsonHierarchyAssociationMessage,
    JsonHierarchyMessage,
)
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConcepSchemeMessage
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflowMessage
from pysdmx.io.json.sdmxjson2.messages.map import (
    JsonMappingMessage,
    JsonRepresentationMapMessage,
)
from pysdmx.io.json.sdmxjson2.messages.org import (
    JsonAgencyMessage,
    JsonProviderMessage,
)
from pysdmx.io.json.sdmxjson2.messages.report import JsonMetadataMessage
from pysdmx.io.json.sdmxjson2.messages.schema import JsonSchemaMessage

deserializers = Deserializers(
    agencies=JsonAgencyMessage,  # type: ignore[arg-type]
    categories=JsonCategorySchemeMessage,  # type: ignore[arg-type]
    codes=JsonCodelistMessage,  # type: ignore[arg-type]
    concepts=JsonConcepSchemeMessage,  # type: ignore[arg-type]
    dataflow=JsonDataflowMessage,  # type: ignore[arg-type]
    providers=JsonProviderMessage,  # type: ignore[arg-type]
    schema=JsonSchemaMessage,  # type: ignore[arg-type]
    hier_assoc=JsonHierarchyAssociationMessage,  # type: ignore[arg-type]
    hierarchy=JsonHierarchyMessage,  # type: ignore[arg-type]
    report=JsonMetadataMessage,  # type: ignore[arg-type]
    mapping=JsonMappingMessage,  # type: ignore[arg-type]
    code_map=JsonRepresentationMapMessage,  # type: ignore[arg-type]
)
