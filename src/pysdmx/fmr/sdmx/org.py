"""Collection of SDMX-JSON schemas for organisations."""

from collections import defaultdict
from typing import Dict, Sequence, Set

from msgspec import Struct

from pysdmx.fmr.sdmx.pa import JsonProvisionAgreement
from pysdmx.model import DataflowRef, Organisation
from pysdmx.util import parse_urn


class JsonDataProviderScheme(Struct, frozen=True):
    """SDMX-JSON payload for a data provider scheme."""

    dataProviders: Sequence[Organisation]

    def __get_df_ref(self, ref: str) -> DataflowRef:
        a = parse_urn(ref)
        return DataflowRef(a.id, a.agency, version=a.version)

    def to_model(
        self, pas: Sequence[JsonProvisionAgreement]
    ) -> Sequence[Organisation]:
        """Converts a JsonDataProviderScheme to a list of Organisations."""
        if pas:
            paprs: Dict[str, Set[DataflowRef]] = defaultdict(set)
            for pa in pas:
                df = self.__get_df_ref(pa.structureUsage)
                pr = pa.dataProvider[pa.dataProvider.rindex(".") + 1 :]
                paprs[pr].add(df)
            return [
                Organisation(
                    p.id, p.name, p.description, p.contacts, list(paprs[p.id])
                )
                for p in self.dataProviders
            ]
        else:
            return self.dataProviders


class JsonDataProviderSchemes(Struct, frozen=True):
    """SDMX-JSON payload for the list of data provider schemes."""

    dataProviderSchemes: Sequence[JsonDataProviderScheme]
    provisionAgreements: Sequence[JsonProvisionAgreement] = ()

    def to_model(self) -> Sequence[Organisation]:
        """Converts a JsonDataProviderSchemes to a list of Organisations."""
        return self.dataProviderSchemes[0].to_model(self.provisionAgreements)


class JsonProviderMessage(Struct, frozen=True):
    """SDMX-JSON payload for /dataproviderscheme queries."""

    data: JsonDataProviderSchemes

    def to_model(self) -> Sequence[Organisation]:
        """Returns the requested list of providers."""
        return self.data.to_model()


class JsonAgencyScheme(Struct, frozen=True):
    """SDMX-JSON payload for an agency scheme."""

    agencyID: str
    agencies: Sequence[Organisation]


class JsonAgencySchemes(Struct, frozen=True):
    """SDMX-JSON payload for the list of agency schemes."""

    agencySchemes: Sequence[JsonAgencyScheme]


class JsonAgencyMessage(Struct, frozen=True):
    """SDMX-JSON payload for /agencyscheme queries."""

    data: JsonAgencySchemes

    def __add_owner(self, owner: str, a: Organisation) -> Organisation:
        oid = f"{owner}.{a.id}" if owner != "SDMX" else a.id
        return Organisation(oid, a.name, a.description, a.contacts)

    def to_model(self) -> Sequence[Organisation]:
        """Returns the requested list of agencies."""
        return [
            self.__add_owner(self.data.agencySchemes[0].agencyID, a)
            for a in self.data.agencySchemes[0].agencies
        ]
