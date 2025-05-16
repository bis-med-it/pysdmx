"""Collection of SDMX-JSON schemas for provision agreements."""

from datetime import datetime
from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation
from pysdmx.model import DataflowRef, ProvisionAgreement
from pysdmx.util import parse_maintainable_urn


class JsonProvisionAgreement(
    Struct, frozen=True, rename={"agency": "agencyID"}
):
    """SDMX-JSON payload for a provision agreement."""

    id: str
    name: str
    agency: str
    dataflow: str
    dataProvider: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None

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
            dataflow=DataflowRef.from_reference(
                parse_maintainable_urn(self.dataflow)
            ),
            provider=self.dataProvider,
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
