"""Collection of GDS-JSON schemas for GDS agencies."""

from typing import Sequence

from msgspec import Struct

from pysdmx.model import Agency


class JsonAgency(Struct, frozen=True):
    """GDS-JSON payload for an agency scheme."""

    agencyID: str
    name: str
    url: str
    description: str = ""

    def to_model(self) -> Agency:
        """Converts the payload to a GDS Agency."""
        return Agency(
            id=self.agencyID,
            name=self.name,
            uri=self.url,
            description=self.description,
        )


class JsonStructures(Struct, frozen=True):
    """Intermediate structure for 'structures' field."""

    agencies: Sequence[JsonAgency]


class JsonAgencyMessage(Struct, frozen=True):
    """GDS-JSON payload for /agency queries."""

    structures: JsonStructures

    def to_model(self) -> Sequence[Agency]:
        """Returns a list with the requested agencies."""
        return [a.to_model() for a in self.structures.agencies]
