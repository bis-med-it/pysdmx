"""Collection of Fusion-JSON schemas for provision agreements."""

from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.model import ProvisionAgreement as PA


class FusionProvisionAgreement(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for a provision agreement."""

    id: str
    names: Sequence[FusionString]
    agency: str
    structureUsage: str
    dataproviderRef: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"

    def to_model(self) -> PA:
        """Converts a JsonPA to a standard provision agreement."""
        description = self.descriptions[0].value if self.descriptions else None
        return PA(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            description=description,
            version=self.version,
            provider=self.dataproviderRef,
            dataflow=self.structureUsage,
        )


class FusionProvisionAgreementMessage(Struct, frozen=True):
    """Fusion-JSON payload for /provisionagreement queries."""

    ProvisionAgreement: Sequence[FusionProvisionAgreement]

    def to_model(self) -> Sequence[PA]:
        """Returns the requested provision agreements."""
        return [c.to_model() for c in self.ProvisionAgreement]
