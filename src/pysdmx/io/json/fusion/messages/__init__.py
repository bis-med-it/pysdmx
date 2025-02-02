"""Schemas for Fusion-JSON messages."""

from pysdmx.io.json.fusion.messages.category import (
    FusionCategorisationMessage,
    FusionCategorySchemeMessage,
)
from pysdmx.io.json.fusion.messages.code import (
    FusionCodelistMessage,
    FusionHierarchyAssociationMessage,
    FusionHierarchyMessage,
)
from pysdmx.io.json.fusion.messages.concept import FusionConceptSchemeMessage
from pysdmx.io.json.fusion.messages.dataflow import (
    FusionDataflowMessage,
    FusionDataflowsMessage,
)
from pysdmx.io.json.fusion.messages.map import (
    FusionMappingMessage,
    FusionRepresentationMapMessage,
)
from pysdmx.io.json.fusion.messages.org import (
    FusionAgencyMessage,
    FusionProviderMessage,
)
from pysdmx.io.json.fusion.messages.pa import (
    FusionProvisionAgreementMessage as FusionPAMessage,
)
from pysdmx.io.json.fusion.messages.report import FusionMetadataMessage
from pysdmx.io.json.fusion.messages.schema import FusionSchemaMessage
from pysdmx.io.json.fusion.messages.vtl import (
    FusionVtlTransformationsMessage as FusionTransfoMsg,
)

__all__ = [
    "FusionCategorisationMessage",
    "FusionCategorySchemeMessage",
    "FusionCodelistMessage",
    "FusionHierarchyAssociationMessage",
    "FusionHierarchyMessage",
    "FusionConceptSchemeMessage",
    "FusionDataflowMessage",
    "FusionDataflowsMessage",
    "FusionMappingMessage",
    "FusionRepresentationMapMessage",
    "FusionAgencyMessage",
    "FusionProviderMessage",
    "FusionMetadataMessage",
    "FusionSchemaMessage",
    "FusionTransfoMsg",
    "FusionPAMessage",
]
