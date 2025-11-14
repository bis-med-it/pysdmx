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
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraintMessage
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
from pysdmx.io.json.sdmxjson2.messages.metadataflow import (
    JsonMetadataflowsMessage as JsonMdfsMsg,
)
from pysdmx.io.json.sdmxjson2.messages.mpa import (
    JsonMetadataProvisionAgreementsMessage as JsonMPAMsg,
)
from pysdmx.io.json.sdmxjson2.messages.msd import JsonMetadataStructuresMessage
from pysdmx.io.json.sdmxjson2.messages.pa import (
    JsonProvisionAgreementsMessage as JsonPAMessage,
)
from pysdmx.io.json.sdmxjson2.messages.provider import (
    JsonMetadataProviderMessage,
    JsonProviderMessage,
)
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
    "JsonDataConstraintMessage",
    "JsonDataflowMessage",
    "JsonDataflowsMessage",
    "JsonDataStructuresMessage",
    "JsonMetadataProviderMessage",
    "JsonProviderMessage",
    "JsonPAMessage",
    "JsonSchemaMessage",
    "JsonHierarchyAssociationMessage",
    "JsonHierarchiesMessage",
    "JsonHierarchyMessage",
    "JsonMdfsMsg",
    "JsonMetadataMessage",
    "JsonMPAMsg",
    "JsonMappingMessage",
    "JsonMetadataStructuresMessage",
    "JsonRepresentationMapMessage",
    "JsonRepresentationMapsMessage",
    "JsonStructureMapsMessage",
    "JsonStructureMessage",
    "JsonTransfoMsg",
]
