"""Collection of SDMX-JSON schemas for dataflow queries."""

from typing import List, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist, JsonValuelist
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConceptScheme
from pysdmx.io.json.sdmxjson2.messages.core import MaintainableType
from pysdmx.io.json.sdmxjson2.messages.dsd import JsonDataStructure
from pysdmx.io.json.sdmxjson2.messages.provider import JsonDataProviderScheme
from pysdmx.model import (
    Agency,
    Components,
    Dataflow,
    DataflowInfo,
    DataProvider,
    DataStructureDefinition,
)
from pysdmx.util import parse_urn


class JsonDataflow(MaintainableType, frozen=True):
    """SDMX-JSON payload for a dataflow."""

    structure: str = ""

    def to_model(
        self,
        dsds: Sequence[JsonDataStructure] = (),
        concepts: Sequence[JsonConceptScheme] = (),
        valuelists: Sequence[JsonValuelist] = (),
        codelists: Sequence[JsonCodelist] = (),
    ) -> Dataflow:
        """Converts a FusionDataflow to a standard dataflow."""
        dsd: Optional[Union[DataStructureDefinition, str]] = None
        if len(dsds) > 0:
            ref = parse_urn(self.structure)
            m = [
                d
                for d in dsds
                if d.agency == ref.agency
                and d.id == ref.id
                and d.version == ref.version
            ]
            if len(m) == 1:
                dsd = m[0].to_model(concepts, codelists, valuelists, ())
        dsd = dsd if dsd is not None else self.structure
        return Dataflow(
            id=self.id,
            agency=self.agency,
            name=self.name,
            description=self.description,
            version=self.version,
            structure=dsd,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )


class JsonDataflows(Struct, frozen=True):
    """SDMX-JSON payload for the list of dataflows."""

    dataflows: Sequence[JsonDataflow]
    dataProviderSchemes: Sequence[JsonDataProviderScheme] = ()
    dataStructures: Sequence[JsonDataStructure] = ()
    conceptSchemes: Sequence[JsonConceptScheme] = ()
    valuelists: Sequence[JsonValuelist] = ()
    codelists: Sequence[JsonCodelist] = ()

    def __filter(
        self, df: JsonDataflow, agency: str, id_: str, version: str
    ) -> bool:
        if version != "+" and version != "latest":
            return (
                df.agency == agency and df.id == id_ and df.version == version
            )
        else:
            return df.agency == agency and df.id == id_

    def to_model(
        self, components: Components, agency: str, id_: str, version: str
    ) -> DataflowInfo:
        """Returns the requested dataflow details."""
        prvs: List[DataProvider] = []
        for dps in self.dataProviderSchemes:
            prvs.extend(dps.dataProviders)
        df = list(
            filter(
                lambda df: self.__filter(df, agency, id_, version),
                self.dataflows,
            )
        )[0]
        return DataflowInfo(
            id=df.id,
            components=components,
            agency=Agency(df.agency),
            name=df.name,
            description=df.description,
            version=df.version,
            providers=prvs,
            dsd_ref=df.structure,
        )

    def to_generic_model(self) -> Sequence[Dataflow]:
        """Returns the requested dataflows."""
        return [
            df.to_model(
                self.dataStructures,
                self.conceptSchemes,
                self.valuelists,
                self.codelists,
            )
            for df in self.dataflows
        ]


class JsonDataflowMessage(Struct, frozen=True):
    """SDMX-JSON payload for /dataflow queries (with details)."""

    data: JsonDataflows

    def to_model(
        self, components: Components, agency: str, id_: str, version: str
    ) -> DataflowInfo:
        """Returns the requested dataflow details."""
        return self.data.to_model(components, agency, id_, version)


class JsonDataflowsMessage(Struct, frozen=True):
    """SDMX-JSON payload for /dataflow queries."""

    data: JsonDataflows

    def to_model(self) -> Sequence[Dataflow]:
        """Returns the requested dataflows."""
        return self.data.to_generic_model()
