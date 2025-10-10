"""Collection of Fusion-JSON schemas for provision agreements."""

from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.model import MetadataProvisionAgreement as MPA


class FusionMetadataProvisionAgreement(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for a metadata provision agreement."""

    id: str
    names: Sequence[FusionString]
    agency: str
    metadataflowRef: str
    metadataproviderRef: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"

    def to_model(self) -> MPA:
        """Converts a JsonPA to a standard provision agreement."""
        description = self.descriptions[0].value if self.descriptions else None
        return MPA(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            description=description,
            version=self.version,
            metadata_provider=self.metadataproviderRef,
            metadataflow=self.metadataflowRef,
        )


class FusionMetadataProvisionAgreementMessage(Struct, frozen=True):
    """Fusion-JSON payload for /metadataprovisionagreement queries."""

    MetadataProvisionAgreement: Sequence[FusionMetadataProvisionAgreement]

    def to_model(self) -> Sequence[MPA]:
        """Returns the requested metadata provision agreements."""
        return [c.to_model() for c in self.MetadataProvisionAgreement]
