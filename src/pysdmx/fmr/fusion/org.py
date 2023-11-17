"""Collection of Fusion-JSON schemas for organisations."""

from collections import defaultdict
from typing import Dict, Optional, Sequence, Set

from msgspec import Struct

from pysdmx.fmr.fusion.core import FusionString
from pysdmx.model import Contact, DataflowRef, Organisation
from pysdmx.util import parse_urn


class FusionContact(Struct, frozen=True):
    """Fusion-JSON payload for a contact."""

    id: Optional[str] = None
    names: Optional[Sequence[FusionString]] = None
    departments: Optional[Sequence[FusionString]] = None
    roles: Optional[Sequence[FusionString]] = None
    telephone: Optional[Sequence[str]] = None
    fax: Optional[Sequence[str]] = None
    uri: Optional[Sequence[str]] = None
    email: Optional[Sequence[str]] = None

    def to_model(self) -> Contact:
        """Converts a FusionContact to a standard Contact."""
        n = self.names[0].value if self.names else None
        d = self.departments[0].value if self.departments else None
        r = self.roles[0].value if self.roles else None

        return Contact(
            self.id,
            n,
            d,
            r,
            self.telephone,
            self.fax,
            self.uri,
            self.email,
        )


class FusionOrg(Struct, frozen=True):
    """Fusion-JSON payload for an organisation."""

    id: str
    names: Sequence[FusionString]
    descriptions: Optional[Sequence[FusionString]] = None
    contacts: Sequence[FusionContact] = ()

    def to_model(self, owner: Optional[str] = None) -> Organisation:
        """Converts a FusionOrg to a standard Organisation."""
        d = self.descriptions[0].value if self.descriptions else None
        c = [c.to_model() for c in self.contacts]
        oid = f"{owner}.{self.id}" if owner and owner != "SDMX" else self.id
        if c:
            return Organisation(oid, self.names[0].value, d, c)
        else:
            return Organisation(oid, self.names[0].value, d)


class FusionAgencyScheme(Struct, frozen=True):
    """Fusion-JSON payload for an agency scheme."""

    agencyId: str
    items: Sequence[FusionOrg]

    def to_model(self) -> Sequence[Organisation]:
        """Converts a FusionAgencyScheme to a list of Organisations."""
        return [o.to_model(self.agencyId) for o in self.items]


class FusionAgencyMessage(Struct, frozen=True):
    """Fusion-JSON payload for /agencyscheme queries."""

    AgencyScheme: Sequence[FusionAgencyScheme]

    def to_model(self) -> Sequence[Organisation]:
        """Returns the requested list of agencies."""
        return self.AgencyScheme[0].to_model()


class FusionProvisionAgreement(Struct, frozen=True):
    """Fusion-JSON payload for a provision agreement."""

    structureUsage: str
    dataproviderRef: str


class FusionProviderScheme(Struct, frozen=True):
    """Fusion-JSON payload for a data provider scheme."""

    items: Sequence[FusionOrg]

    def __get_df_ref(self, ref: str) -> DataflowRef:
        a = parse_urn(ref)
        return DataflowRef(a.id, a.agency, version=a.version)

    def to_model(
        self, pas: Sequence[FusionProvisionAgreement]
    ) -> Sequence[Organisation]:
        """Converts a FusionProviderScheme to a list of Organisations."""
        if pas:
            paprs: Dict[str, Set[DataflowRef]] = defaultdict(set)
            for pa in pas:
                df = self.__get_df_ref(pa.structureUsage)
                pr = pa.dataproviderRef[pa.dataproviderRef.rindex(".") + 1 :]
                paprs[pr].add(df)
            prvs = [o.to_model() for o in self.items]
            return [
                Organisation(
                    p.id, p.name, p.description, p.contacts, list(paprs[p.id])
                )
                for p in prvs
            ]
        else:
            return [o.to_model() for o in self.items]


class FusionProviderMessage(Struct, frozen=True):
    """Fusion-JSON payload for /dataproviderscheme queries."""

    DataProviderScheme: Sequence[FusionProviderScheme]
    ProvisionAgreement: Sequence[FusionProvisionAgreement] = ()

    def to_model(self) -> Sequence[Organisation]:
        """Returns the requested list of providers."""
        return self.DataProviderScheme[0].to_model(self.ProvisionAgreement)
