"""Collection of Fusion-JSON schemas for dataflow queries."""

from typing import List, Optional, Sequence

from msgspec import Struct

from pysdmx.fmr.fusion.core import FusionString
from pysdmx.fmr.fusion.org import FusionProviderScheme
from pysdmx.model import Components, DataflowInfo, DataflowRef, Organisation


class FusionDataflowRef(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a dataflow."""

    id: str
    agency: str
    names: Sequence[FusionString]
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"

    def to_model(self) -> DataflowRef:
        """Converts a FusionDataflowRef to a standard dataflow ref."""
        return DataflowRef(
            self.id,
            self.agency,
            self.names[0].value if self.names else None,
            self.descriptions[0].value if self.descriptions else None,
            self.version,
        )


class FusionDataflow(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a dataflow."""

    id: str
    names: Sequence[FusionString]
    agency: str
    dataStructureRef: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"


class FusionDataflowMessage(Struct, frozen=True):
    """Fusion-JSON payload for /dataflow queries."""

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
        prvs: List[Organisation] = []
        for dps in self.DataProviderScheme:
            prvs.extend(dps.to_model([]))
        df = list(
            filter(
                lambda df: self.__filter(df, agency, id_, version),
                self.Dataflow,
            )
        )[0]
        return DataflowInfo(
            df.id,
            components,
            Organisation(df.agency),
            df.names[0].value,
            df.descriptions[0].value if df.descriptions else None,
            df.version,
            prvs,
            dsd_ref=df.dataStructureRef,
        )
