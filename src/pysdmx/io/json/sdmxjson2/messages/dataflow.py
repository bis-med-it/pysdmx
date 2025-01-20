"""Collection of SDMX-JSON schemas for dataflow queries."""

from datetime import datetime
from typing import List, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation
from pysdmx.io.json.sdmxjson2.messages.org import JsonDataProviderScheme
from pysdmx.model import (
    Agency,
    Components,
    Dataflow,
    DataflowInfo,
    DataProvider,
)


class JsonDataflow(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a dataflow."""

    id: str
    name: str
    agency: str
    structure: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None

    def to_model(self) -> Dataflow:
        """Converts a FusionDataflow to a standard dataflow."""
        return Dataflow(
            id=self.id,
            agency=self.agency,
            name=self.name,
            description=self.description,
            version=self.version,
            structure=self.structure,
        )


class JsonDataflows(Struct, frozen=True):
    """SDMX-JSON payload for the list of dataflows."""

    dataflows: Sequence[JsonDataflow]
    dataProviderSchemes: Sequence[JsonDataProviderScheme] = ()

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

    def to_simple_model(self) -> Sequence[Dataflow]:
        """Returns the requested dataflows."""
        return [df.to_model() for df in self.dataflows]


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
        return self.data.to_simple_model()
