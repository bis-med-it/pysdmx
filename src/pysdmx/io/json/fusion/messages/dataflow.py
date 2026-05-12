"""Collection of Fusion-JSON schemas for dataflow queries."""

import re
from typing import List, Optional, Sequence

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.io.json.fusion.messages.org import FusionProviderScheme
from pysdmx.model import (
    Agency,
    Components,
    DataflowInfo,
    DataProvider,
)
from pysdmx.model import (
    Dataflow as DF,
)
from pysdmx.model.dataflow import Group
from pysdmx.util import semver_final_pattern


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
        if version not in ["~", "+", "latest"]:
            return (
                df.agency == agency and df.id == id_ and df.version == version
            )
        elif version == "+":
            return (
                df.agency == agency
                and df.id == id_
                and bool(semver_final_pattern.fullmatch(df.version))
            )
        else:
            return df.agency == agency and df.id == id_

    def to_model(
        self,
        components: Components,
        grps: Optional[Sequence[Group]],
        agency: str,
        id_: str,
        version: str,
    ) -> DataflowInfo:
        """Returns the requested dataflow details."""
        prvs: List[DataProvider] = []
        for dps in self.DataProviderScheme:
            prvs.extend(dps.to_model([]))
        dfs = list(
            filter(
                lambda df: self.__filter(df, agency, id_, version),
                self.Dataflow,
            )
        )

        if not dfs:
            raise errors.NotFound(
                "No matching dataflow",
                "No matching dataflow was found in the message",
                {"agency": agency, "id": id, "version": version},
            )

        df = dfs[0]

        return DataflowInfo(
            id=df.id,
            components=components,
            agency=Agency(df.agency),
            name=df.names[0].value,
            description=df.descriptions[0].value if df.descriptions else None,
            version=df.version,
            providers=prvs,
            dsd_ref=df.dataStructureRef,
            groups=grps,
        )


class FusionDataflowsMessage(Struct, frozen=True):
    """Fusion-JSON payload for /dataflow queries."""

    Dataflow: Sequence[FusionDataflow]

    def to_model(self) -> Sequence[DF]:
        """Returns the requested dataflow details."""
        return [df.to_model() for df in self.Dataflow]
