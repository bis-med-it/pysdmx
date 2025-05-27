"""Collection of SDMX-JSON schemas for provision agreements."""

from typing import Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import (
    MaintainableType,
)
from pysdmx.model import ProvisionAgreement


class JsonProvisionAgreement(MaintainableType, frozen=True):
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
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
        )


class JsonProvisionAgreements(Struct, frozen=True):
    """SDMX-JSON payload for provision agreements."""

    provisionAgreements: Sequence[JsonProvisionAgreement]

    def to_model(self) -> Sequence[ProvisionAgreement]:
        """Returns the requested provision agreements."""
        return [pa.to_model() for pa in self.provisionAgreements]


class JsonProvisionAgreementsMessage(Struct, frozen=True):
    """SDMX-JSON payload for /provisionagreement queries."""

    data: JsonProvisionAgreements

    def to_model(self) -> Sequence[ProvisionAgreement]:
        """Returns the requested provision agreements."""
        return self.data.to_model()
