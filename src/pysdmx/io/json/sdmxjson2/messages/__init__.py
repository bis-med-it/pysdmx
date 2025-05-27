"""Schemas for SDMX-JSON messages."""

from pysdmx.io.json.sdmxjson2.messages.agency import JsonAgencyMessage
from pysdmx.io.json.sdmxjson2.messages.category import (
    JsonCategorisationMessage,
    JsonCategorySchemeMessage,
)
from pysdmx.io.json.sdmxjson2.messages.code import (
    JsonCodelistMessage,
    JsonHierarchiesMessage,
    JsonHierarchyAssociationMessage,
    JsonHierarchyMessage,
)
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConceptSchemeMessage
from pysdmx.io.json.sdmxjson2.messages.dataflow import (
    JsonDataflowMessage,
    JsonDataflowsMessage,
)
from pysdmx.io.json.sdmxjson2.messages.dsd import JsonDataStructuresMessage
from pysdmx.io.json.sdmxjson2.messages.map import (
    JsonMappingMessage,
    JsonRepresentationMapMessage,
    JsonRepresentationMapsMessage,
    JsonStructureMapsMessage,
)
from pysdmx.io.json.sdmxjson2.messages.pa import (
    JsonProvisionAgreementsMessage as JsonPAMessage,
)
from pysdmx.io.json.sdmxjson2.messages.provider import JsonProviderMessage
from pysdmx.io.json.sdmxjson2.messages.report import JsonMetadataMessage
from pysdmx.io.json.sdmxjson2.messages.schema import JsonSchemaMessage
from pysdmx.io.json.sdmxjson2.messages.structure import JsonStructureMessage
from pysdmx.io.json.sdmxjson2.messages.vtl import (
    JsonVtlTransformationsMessage as JsonTransfoMsg,
)

__all__ = [
    "JsonAgencyMessage",
    "JsonCategorisationMessage",
    "JsonCategorySchemeMessage",
    "JsonCodelistMessage",
    "JsonConceptSchemeMessage",
    "JsonDataflowMessage",
    "JsonDataflowsMessage",
    "JsonDataStructuresMessage",
    "JsonProviderMessage",
    "JsonPAMessage",
    "JsonSchemaMessage",
    "JsonHierarchyAssociationMessage",
    "JsonHierarchiesMessage",
    "JsonHierarchyMessage",
    "JsonMetadataMessage",
    "JsonMappingMessage",
    "JsonRepresentationMapMessage",
    "JsonRepresentationMapsMessage",
    "JsonStructureMapsMessage",
    "JsonStructureMessage",
    "JsonTransfoMsg",
]
