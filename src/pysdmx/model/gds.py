from msgspec import Struct

from pysdmx.model import Agency, AgencyScheme as AS


class GdsAgency(Struct, frozen=True):
    """
    Represents a GDS agency.
    Attributes:
        agencyId: The ID of the agency.
        name: The name of the agency.
        url: The URL of the agency.
        description: An optional description of the agency.
    """

    agencyId: str
    name: str
    url: str
    description: Optional[str] = None

    def to_model(self, owner: Optional[str] = None) -> Agency:
        """Converts a GdsOrg to a standard Organisation."""
        d = self.description
        oid = f"{owner}.{self.code}" if owner and owner != "SDMX" else self.code
        return Agency(id=oid, name=self.name, description=d, contacts=None)
