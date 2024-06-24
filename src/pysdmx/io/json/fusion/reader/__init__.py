"""Collection of readers for Fusion-JSON messages."""

from pysdmx.api.fmr.reader import Deserializers
from pysdmx.io.json.fusion import messages as msg

deserializers = Deserializers(
    agencies=msg.FusionAgencyMessage,  # type: ignore[arg-type]
    categories=msg.FusionCategorySchemeMessage,  # type: ignore[arg-type]
    codes=msg.FusionCodelistMessage,  # type: ignore[arg-type]
    concepts=msg.FusionConceptSchemeMessage,  # type: ignore[arg-type]
    dataflow=msg.FusionDataflowMessage,  # type: ignore[arg-type]
    providers=msg.FusionProviderMessage,  # type: ignore[arg-type]
    schema=msg.FusionSchemaMessage,  # type: ignore[arg-type]
    hier_assoc=msg.FusionHierarchyAssociationMessage,  # type: ignore[arg-type]
    hierarchy=msg.FusionHierarchyMessage,  # type: ignore[arg-type]
    report=msg.FusionMetadataMessage,  # type: ignore[arg-type]
    mapping=msg.FusionMappingMessage,  # type: ignore[arg-type]
    code_map=msg.FusionRepresentationMapMessage,  # type: ignore[arg-type]
)
