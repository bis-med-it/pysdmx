"""Collection of Fusion-JSON schemas for dataflow queries."""

from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.model import Metadataflow as MDF


class FusionMetadataflow(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a metadataflow."""

    id: str
    agency: str
    names: Sequence[FusionString]
    metadataStructureRef: str
    targets: Sequence[str]
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"

    def to_model(self) -> MDF:
        """Converts a FusionMetadataflow to a standard metadataflow."""
        return MDF(
            id=self.id,
            agency=self.agency,
            name=self.names[0].value if self.names else None,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            structure=self.metadataStructureRef,
            targets=self.targets,
        )


class FusionMetadataflowsMessage(Struct, frozen=True):
    """Fusion-JSON payload for /metadataflow queries."""

    Metadataflow: Sequence[FusionMetadataflow]

    def to_model(self) -> Sequence[MDF]:
        """Returns the requested metadataflow details."""
        return [df.to_model() for df in self.Metadataflow]
