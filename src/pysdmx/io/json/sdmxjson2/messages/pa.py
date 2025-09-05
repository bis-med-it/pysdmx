"""Collection of SDMX-JSON schemas for provision agreements."""

from typing import Sequence

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    MaintainableType,
)
from pysdmx.model import Agency, ProvisionAgreement


class JsonProvisionAgreement(
    MaintainableType, frozen=True, omit_defaults=True
):
    """SDMX-JSON payload for a provision agreement."""

    dataflow: str = ""
    dataProvider: str = ""

    def to_model(self) -> ProvisionAgreement:
        """Converts a FusionPA to a standard provision agreement."""
        return ProvisionAgreement(
            id=self.id,
            agency=self.agency,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            dataflow=self.dataflow,
            provider=self.dataProvider,
            annotations=tuple([a.to_model() for a in self.annotations]),
            is_external_reference=self.isExternalReference,
        )

    @classmethod
    def from_model(self, pa: ProvisionAgreement) -> "JsonProvisionAgreement":
        """Converts a pysdmx provision agreement to an SDMX-JSON one."""
        if not pa.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON provision agreements must have a name",
                {"provision_agreement": pa.id},
            )
        return JsonProvisionAgreement(
            agency=(
                pa.agency.id if isinstance(pa.agency, Agency) else pa.agency
            ),
            id=pa.id,
            name=pa.name,
            version=pa.version,
            isExternalReference=pa.is_external_reference,
            validFrom=pa.valid_from,
            validTo=pa.valid_to,
            description=pa.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in pa.annotations]
            ),
            dataflow=pa.dataflow,
            dataProvider=pa.provider,
        )


class JsonProvisionAgreements(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for provision agreements."""

    provisionAgreements: Sequence[JsonProvisionAgreement]

    def to_model(self) -> Sequence[ProvisionAgreement]:
        """Returns the requested provision agreements."""
        return [pa.to_model() for pa in self.provisionAgreements]


class JsonProvisionAgreementsMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /provisionagreement queries."""

    data: JsonProvisionAgreements

    def to_model(self) -> Sequence[ProvisionAgreement]:
        """Returns the requested provision agreements."""
        return self.data.to_model()
