"""Collection of SDMX-JSON schemas for provision agreements."""

from typing import Sequence

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    MaintainableType,
)
from pysdmx.model import Agency, MetadataProvisionAgreement


class JsonMetadataProvisionAgreement(
    MaintainableType, frozen=True, omit_defaults=True
):
    """SDMX-JSON payload for a metadata provision agreement."""

    metadataflow: str = ""
    metadataProvider: str = ""

    def to_model(self) -> MetadataProvisionAgreement:
        """Converts a FusionPA to a standard metadata provision agreement."""
        return MetadataProvisionAgreement(
            id=self.id,
            agency=self.agency,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            metadataflow=self.metadataflow,
            metadata_provider=self.metadataProvider,
            annotations=tuple([a.to_model() for a in self.annotations]),
            is_external_reference=self.isExternalReference,
        )

    @classmethod
    def from_model(
        self, mpa: MetadataProvisionAgreement
    ) -> "JsonMetadataProvisionAgreement":
        """Converts a pysdmx metadata provision agreement to SDMX-JSON."""
        if not mpa.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON metadata provision agreements must have a name",
                {"metadata_provision_agreement": mpa.id},
            )
        return JsonMetadataProvisionAgreement(
            agency=(
                mpa.agency.id if isinstance(mpa.agency, Agency) else mpa.agency
            ),
            id=mpa.id,
            name=mpa.name,
            version=mpa.version,
            isExternalReference=mpa.is_external_reference,
            validFrom=mpa.valid_from,
            validTo=mpa.valid_to,
            description=mpa.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in mpa.annotations]
            ),
            metadataflow=mpa.metadataflow,
            metadataProvider=mpa.metadata_provider,
        )


class JsonMetadataProvisionAgreements(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for provision agreements."""

    metadataProvisionAgreements: Sequence[JsonMetadataProvisionAgreement]

    def to_model(self) -> Sequence[MetadataProvisionAgreement]:
        """Returns the requested metadata provision agreements."""
        return [pa.to_model() for pa in self.metadataProvisionAgreements]


class JsonMetadataProvisionAgreementsMessage(
    Struct, frozen=True, omit_defaults=True
):
    """SDMX-JSON payload for /metadataprovisionagreement queries."""

    data: JsonMetadataProvisionAgreements

    def to_model(self) -> Sequence[MetadataProvisionAgreement]:
        """Returns the requested metadata provision agreements."""
        return self.data.to_model()
