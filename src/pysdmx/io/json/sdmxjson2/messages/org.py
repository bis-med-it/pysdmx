"""Collection of SDMX-JSON schemas for organisations."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional, Sequence, Set

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    ItemSchemeType,
)
from pysdmx.io.json.sdmxjson2.messages.pa import JsonProvisionAgreement
from pysdmx.model import (
    Agency,
    AgencyScheme,
    DataflowRef,
    DataProvider,
    DataProviderScheme,
)
from pysdmx.util import parse_item_urn, parse_urn


class JsonDataProviderScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for a data provider scheme."""

    dataProviders: Sequence[DataProvider] = ()

    def __get_df_ref(self, ref: str) -> DataflowRef:
        a = parse_urn(ref)
        return DataflowRef(id=a.id, agency=a.agency, version=a.version)

    def to_model(
        self, pas: Sequence[JsonProvisionAgreement]
    ) -> DataProviderScheme:
        """Converts a JsonDataProviderScheme to a list of Organisations."""
        if pas:
            paprs: Dict[str, Set[DataflowRef]] = defaultdict(set)
            for pa in pas:
                df = self.__get_df_ref(pa.dataflow)
                ref = parse_item_urn(pa.dataProvider)
                paprs[f"{ref.agency}:{ref.item_id}"].add(df)
            provs = [
                DataProvider(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    contacts=p.contacts,
                    dataflows=list(paprs[f"{self.agency}:{p.id}"]),
                )
                for p in self.dataProviders
            ]
        else:
            provs = self.dataProviders
        return DataProviderScheme(
            agency=self.agency,
            name=self.name,
            description=self.description,
            items=provs,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )


class JsonDataProviderSchemes(Struct, frozen=True):
    """SDMX-JSON payload for the list of data provider schemes."""

    dataProviderSchemes: Sequence[JsonDataProviderScheme]
    provisionAgreements: Sequence[JsonProvisionAgreement] = ()

    def to_model(self) -> Sequence[DataProviderScheme]:
        """Converts a JsonDataProviderSchemes to a list of Organisations."""
        return [
            s.to_model(self.provisionAgreements)
            for s in self.dataProviderSchemes
        ]


class JsonProviderMessage(Struct, frozen=True):
    """SDMX-JSON payload for /dataproviderscheme queries."""

    data: JsonDataProviderSchemes

    def to_model(self) -> Sequence[DataProviderScheme]:
        """Returns the requested list of data provider schemes."""
        return self.data.to_model()


class JsonAgencyScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for an agency scheme."""

    agencies: Sequence[Agency] = ()

    def __add_owner(self, owner: str, a: Agency) -> Agency:
        oid = f"{owner}.{a.id}" if owner != "SDMX" else a.id
        return Agency(
            id=oid, name=a.name, description=a.description, contacts=a.contacts
        )

    def to_model(self) -> AgencyScheme:
        """Returns the requested list of agencies."""
        agencies = [self.__add_owner(self.agency, a) for a in self.agencies]
        return AgencyScheme(
            description=self.description,
            agency=self.agency,
            items=agencies,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )


class JsonAgencySchemes(Struct, frozen=True):
    """SDMX-JSON payload for the list of agency schemes."""

    agencySchemes: Sequence[JsonAgencyScheme]

    def to_model(self) -> Sequence[AgencyScheme]:
        """Returns the requested agency schemes."""
        return [a.to_model() for a in self.agencySchemes]


class JsonAgencyMessage(Struct, frozen=True):
    """SDMX-JSON payload for /agencyscheme queries."""

    data: JsonAgencySchemes

    def to_model(self) -> Sequence[AgencyScheme]:
        """Returns the requested agency schemes."""
        return self.data.to_model()
