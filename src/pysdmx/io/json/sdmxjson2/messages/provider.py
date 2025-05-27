"""Collection of SDMX-JSON schemas for organisations."""

from collections import defaultdict
from typing import Dict, Sequence, Set

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import ItemSchemeType
from pysdmx.io.json.sdmxjson2.messages.pa import JsonProvisionAgreement
from pysdmx.model import DataflowRef, DataProvider, DataProviderScheme
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
                    annotations=[a.to_model() for a in self.annotations],
                )
                for p in self.dataProviders
            ]
        else:
            provs = [
                DataProvider(
                    id=p.id,
                    name=p.name,
                    description=p.description,
                    contacts=p.contacts,
                    annotations=[a.to_model() for a in self.annotations],
                )
                for p in self.dataProviders
            ]
        return DataProviderScheme(
            agency=self.agency,
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
