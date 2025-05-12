from typing import Optional

from msgspec import Struct

from pysdmx.model import Agency


class GdsAgency(Struct, frozen=True):
    """Represents a GDS agency.
    Attributes:
        agencyId: The ID of the agency.
        name: The name of the agency.
        url: The URL of the agency.
        description: An optional description of the agency.
    """

    agencyId: str
    name: str
    url: str
    description: str = ""

    def to_model(self, owner: Optional[str] = None) -> Agency:
        """Converts a GdsOrg to a standard Organisation."""
        d = self.description
        oid = f"{owner}.{self.agencyId}" if owner and owner != "SDMX" else self.agencyId
        return Agency(id=oid, name=self.name, description=d, contacts=None)
