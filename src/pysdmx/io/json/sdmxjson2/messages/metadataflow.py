"""Collection of SDMX-JSON schemas for dataflow queries."""

from typing import Sequence

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    MaintainableType,
)
from pysdmx.model import Agency, Metadataflow, MetadataStructure


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

    @classmethod
    def from_model(self, df: Metadataflow) -> "JsonMetadataflow":
        """Converts a pysdmx metadataflow to an SDMX-JSON one."""
        if not df.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON metadataflows must have a name",
                {"metadataflow": df.id},
            )
        if isinstance(df.structure, MetadataStructure):
            dsdref = (
                "urn:sdmx:org.sdmx.infomodel.metadatastructure.MetadataStructure="
                f"{df.structure.agency}:{df.structure.id}({df.structure.version})"
            )
        else:
            dsdref = df.structure
        return JsonMetadataflow(
            agency=(
                df.agency.id if isinstance(df.agency, Agency) else df.agency
            ),
            id=df.id,
            name=df.name,
            version=df.version,
            isExternalReference=df.is_external_reference,
            validFrom=df.valid_from,
            validTo=df.valid_to,
            description=df.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in df.annotations]
            ),
            structure=dsdref,
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
