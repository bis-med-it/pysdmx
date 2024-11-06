"""Collection of SDMX-JSON schemas for organisations."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional, Sequence, Set

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation
from pysdmx.io.json.sdmxjson2.messages.pa import JsonProvisionAgreement
from pysdmx.model import Agency, DataflowRef, DataProvider
from pysdmx.util import parse_urn


class JsonDataProviderScheme(Struct, frozen=True):
    """SDMX-JSON payload for a data provider scheme."""

    agencyID: str
    dataProviders: Sequence[DataProvider]
    description: Optional[str] = None
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
    isPartial: bool = False

    def __get_df_ref(self, ref: str) -> DataflowRef:
        a = parse_urn(ref)
        return DataflowRef(id=a.id, agency=a.agency, version=a.version)

    def to_model(
        self, pas: Sequence[JsonProvisionAgreement]
    ) -> Sequence[DataProvider]:
        """Converts a JsonDataProviderScheme to a list of Organisations."""
        if pas:
            paprs: Dict[str, Set[DataflowRef]] = defaultdict(set)
            for pa in pas:
                df = self.__get_df_ref(pa.dataflow)
                pr = pa.dataProvider[pa.dataProvider.rindex(".") + 1 :]
                paprs[pr].add(df)
            return [
                DataProvider(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    contacts=p.contacts,
                    dataflows=list(paprs[p.id]),
                )
                for p in self.dataProviders
            ]
        else:
            return self.dataProviders


class JsonDataProviderSchemes(Struct, frozen=True):
    """SDMX-JSON payload for the list of data provider schemes."""

    dataProviderSchemes: Sequence[JsonDataProviderScheme]
    provisionAgreements: Sequence[JsonProvisionAgreement] = ()

    def to_model(self) -> Sequence[DataProvider]:
        """Converts a JsonDataProviderSchemes to a list of Organisations."""
        return self.dataProviderSchemes[0].to_model(self.provisionAgreements)


class JsonProviderMessage(Struct, frozen=True):
    """SDMX-JSON payload for /dataproviderscheme queries."""

    data: JsonDataProviderSchemes

    def to_model(self) -> Sequence[DataProvider]:
        """Returns the requested list of providers."""
        return self.data.to_model()


class JsonAgencyScheme(Struct, frozen=True):
    """SDMX-JSON payload for an agency scheme."""

    agencyID: str
    agencies: Sequence[Agency]
    description: Optional[str] = None
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
    isPartial: bool = False


class JsonAgencySchemes(Struct, frozen=True):
    """SDMX-JSON payload for the list of agency schemes."""

    agencySchemes: Sequence[JsonAgencyScheme]


class JsonAgencyMessage(Struct, frozen=True):
    """SDMX-JSON payload for /agencyscheme queries."""

    data: JsonAgencySchemes

    def __add_owner(self, owner: str, a: Agency) -> Agency:
        oid = f"{owner}.{a.id}" if owner != "SDMX" else a.id
        return Agency(
            id=oid, name=a.name, description=a.description, contacts=a.contacts
        )

    def to_model(self) -> Sequence[Agency]:
        """Returns the requested list of agencies."""
        return [
            self.__add_owner(self.data.agencySchemes[0].agencyID, a)
            for a in self.data.agencySchemes[0].agencies
        ]
