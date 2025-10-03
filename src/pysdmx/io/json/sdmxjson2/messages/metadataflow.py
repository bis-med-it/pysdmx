"""Collection of SDMX-JSON schemas for dataflow queries."""

from typing import Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import MaintainableType
from pysdmx.model import Metadataflow


class JsonMetadataflow(MaintainableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a metadataflow."""

    structure: str = ""
    targets: Sequence[str] = ()

    def to_model(self) -> Metadataflow:
        """Converts a FusionMetadataflow to a standard one."""
        return Metadataflow(
            id=self.id,
            agency=self.agency,
            name=self.name,
            description=self.description,
            version=self.version,
            structure=self.structure,
            targets=self.targets,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )


class JsonMetadataflows(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of metadataflows."""

    metadataflows: Sequence[JsonMetadataflow]

    def to_model(self) -> Sequence[Metadataflow]:
        """Returns the requested metadataflows."""
        return [mdf.to_model() for mdf in self.metadataflows]


class JsonMetadataflowsMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /metadataflow queries."""

    data: JsonMetadataflows

    def to_model(self) -> Sequence[Metadataflow]:
        """Returns the requested dataflows."""
        return self.data.to_model()
