"""Collection of SDMX-JSON schemas for dataflow queries."""

from typing import List, Optional, Sequence

from msgspec import Struct

from pysdmx.fmr.sdmx.org import JsonDataProviderScheme
from pysdmx.model import (
    Agency,
    Components,
    DataflowInfo,
    DataflowRef,
    DataProvider,
)


class JsonDataflowRef(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a dataflow."""

    id: str
    agency: str
    name: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0"

    def to_model(self) -> DataflowRef:
        """Converts a JsonDataflowRef to a standard dataflow ref."""
        return DataflowRef(
            self.id,
            self.agency,
            self.name,
            self.description,
            self.version,
        )


class JsonDataflow(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a dataflow."""

    id: str
    name: str
    agency: str
    structure: str
    description: Optional[str] = None
    version: str = "1.0"


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
            df.id,
            components,
            Agency(df.agency),
            df.name,
            df.description,
            df.version,
            prvs,
            dsd_ref=df.structure,
        )


class JsonDataflowMessage(Struct, frozen=True):
    """SDMX-JSON payload for /dataflow queries."""

    data: JsonDataflows

    def to_model(
        self, components: Components, agency: str, id_: str, version: str
    ) -> DataflowInfo:
        """Returns the requested dataflow details."""
        return self.data.to_model(components, agency, id_, version)
