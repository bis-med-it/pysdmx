"""Collection of Fusion-JSON schemas for dataflow queries."""

from typing import List, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.io.json.fusion.messages.org import FusionProviderScheme
from pysdmx.model import (
    Agency,
    Components,
    Dataflow as DF,
    DataflowInfo,
    DataProvider,
)


class FusionDataflow(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a dataflow."""

    id: str
    agency: str
    names: Sequence[FusionString]
    dataStructureRef: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"

    def to_model(self) -> DF:
        """Converts a FusionDataflow to a standard dataflow."""
        return DF(
            id=self.id,
            agency=self.agency,
            name=self.names[0].value if self.names else None,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            structure=self.dataStructureRef,
        )


class FusionDataflowMessage(Struct, frozen=True):
    """Fusion-JSON payload for /dataflow queries, with details."""

    Dataflow: Sequence[FusionDataflow]
    DataProviderScheme: Sequence[FusionProviderScheme] = ()

    def __filter(
        self,
        df: FusionDataflow,
        agency: str,
        id_: str,
        version: str,
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
        for dps in self.DataProviderScheme:
            prvs.extend(dps.to_model([]))
        df = list(
            filter(
                lambda df: self.__filter(df, agency, id_, version),
                self.Dataflow,
            )
        )[0]
        return DataflowInfo(
            id=df.id,
            components=components,
            agency=Agency(df.agency),
            name=df.names[0].value,
            description=df.descriptions[0].value if df.descriptions else None,
            version=df.version,
            providers=prvs,
            dsd_ref=df.dataStructureRef,
        )


class FusionDataflowsMessage(Struct, frozen=True):
    """Fusion-JSON payload for /dataflow queries."""

    Dataflow: Sequence[FusionDataflow]

    def to_model(self) -> Sequence[DF]:
        """Returns the requested dataflow details."""
        return [df.to_model() for df in self.Dataflow]
