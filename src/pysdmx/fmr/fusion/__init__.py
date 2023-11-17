"""Collection of Fusion-JSON schemas for the metadata queries."""

from pysdmx.fmr.fusion.category import FusionCategorySchemeMessage
from pysdmx.fmr.fusion.code import (
    FusionCodelistMessage,
    FusionHierarchyMessage,
)
from pysdmx.fmr.fusion.concept import FusionConcepSchemeMessage
from pysdmx.fmr.fusion.dataflow import FusionDataflowMessage
from pysdmx.fmr.fusion.map import (
    FusionMappingMessage,
    FusionRepresentationMapMessage,
)
from pysdmx.fmr.fusion.org import FusionAgencyMessage, FusionProviderMessage
from pysdmx.fmr.fusion.report import FusionMetadataMessage
from pysdmx.fmr.fusion.schema import FusionSchemaMessage
from pysdmx.fmr.reader import Deserializers

deserializers = Deserializers(
    agencies=FusionAgencyMessage,  # type: ignore[arg-type]
    categories=FusionCategorySchemeMessage,  # type: ignore[arg-type]
    codes=FusionCodelistMessage,  # type: ignore[arg-type]
    concepts=FusionConcepSchemeMessage,  # type: ignore[arg-type]
    dataflow=FusionDataflowMessage,  # type: ignore[arg-type]
    providers=FusionProviderMessage,  # type: ignore[arg-type]
    schema=FusionSchemaMessage,  # type: ignore[arg-type]
    hierarchy=FusionHierarchyMessage,  # type: ignore[arg-type]
    report=FusionMetadataMessage,  # type: ignore[arg-type]
    mapping=FusionMappingMessage,  # type: ignore[arg-type]
    code_map=FusionRepresentationMapMessage,  # type: ignore[arg-type]
)
