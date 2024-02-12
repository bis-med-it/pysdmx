"""Collection of SDMX-JSON schemas for the metadata queries."""

from pysdmx.fmr.reader import Deserializers
from pysdmx.fmr.sdmx.category import JsonCategorySchemeMessage
from pysdmx.fmr.sdmx.code import (
    JsonCodelistMessage,
    JsonHierarchyAssociationMessage,
    JsonHierarchyMessage,
)
from pysdmx.fmr.sdmx.concept import JsonConcepSchemeMessage
from pysdmx.fmr.sdmx.dataflow import JsonDataflowMessage
from pysdmx.fmr.sdmx.map import (
    JsonMappingMessage,
    JsonRepresentationMapMessage,
)
from pysdmx.fmr.sdmx.org import JsonAgencyMessage, JsonProviderMessage
from pysdmx.fmr.sdmx.report import JsonMetadataMessage
from pysdmx.fmr.sdmx.schema import JsonSchemaMessage

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
