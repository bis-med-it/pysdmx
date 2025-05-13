"""Collection of SDMX-JSON schemas for GDS agencies."""

from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.model import Agency, AgencyScheme
from pysdmx.model.gds import GdsAgency


class JsonAgency(Struct, frozen=True):
    """SDMX-JSON payload for an agency scheme."""
    agencyID: str
    name: str
    url: str
    description: str = ""

    def to_model(self) -> Agency:
        """Converts the payload to a Gds Agency."""
        return GdsAgency(
            agencyId=self.agencyID,
            name=self.name,
            url=self.url,
            description=self.description
        )

    def to_sdmx_model(self, owner: Optional[str] = None) -> Agency:
        """Converts a Gds Agency to a standard Organisation."""
        d = self.description
        oid = f"{owner}.{self.agencyID}" if (owner and
                 owner != "SDMX") else self.agencyID
        return Agency(id=oid, name=self.name, description=d, contacts=None)


class JsonStructures(Struct, frozen=True):
    """Intermediate structure for 'structures' field."""
    agencies: Sequence[JsonAgency]


class JsonAgencyMessage(Struct, frozen=True):
    """SDMX-JSON payload for /agency queries."""
    structures: JsonStructures

    def to_model(self) -> Sequence[AgencyScheme]:
        """Returns a list with the requested agencies."""
        return [a.to_model() for a in self.structures.agencies]
