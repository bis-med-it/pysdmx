from msgspec import Struct

from pysdmx.model import Agency, AgencyScheme as AS


class GdsAgency(Struct, frozen=True):
    """
    Represents a GDS agency.
    Attributes:
        name: The name of the agency.
        description: A description of the agency.
        url: The URL of the agency's website.
        code: The code of the agency.
    """

    name: str
    code: str
    url: str
    description: Optional[str] = None

    def to_model(self, owner: Optional[str] = None) -> Agency:
        """Converts a GdsOrg to a standard Organisation."""
        d = self.description
        oid = f"{owner}.{self.code}" if owner and owner != "SDMX" else self.code
        return Agency(id=oid, name=self.name, description=d, contacts=None)


class AgencyScheme(Struct, frozen=True):
    """Gds-JSON payload for an agency scheme."""

    code: str
    descriptions: Sequence[str] = ()
    items: Sequence[GdsAgency] = ()

    def to_model(self) -> AS:
        """Converts a GdsAS to a list of Organisations."""
        agencies = [o.to_model(self.code) for o in self.items]
        return AS(
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            agency=self.code,
            items=agencies,
        )


class GdsAgencyMessage(Struct, frozen=True):
    """Gds-JSON payload for /agency queries."""

    AgencyScheme: Sequence[AgencyScheme]

    def to_model(self) -> Sequence[AS]:
        """Returns the requested agency schemes."""
        return [a.to_model() for a in self.AgencyScheme]
