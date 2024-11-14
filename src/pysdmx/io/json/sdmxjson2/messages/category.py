"""Collection of SDMX-JSON schemas for categories and category schemes."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflowRef
from pysdmx.model import Category, CategoryScheme, DataflowRef
from pysdmx.util import find_by_urn


class JsonCategorisation(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a categorisation."""

    id: str
    name: str
    agency: str
    source: str
    target: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None


class JsonCategoryScheme(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a category scheme."""

    id: str
    name: str
    agency: str
    description: Optional[str] = None
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    annotations: Optional[Sequence[JsonAnnotation]] = None
    categories: Sequence[Category] = ()

    def to_model(self) -> CategoryScheme:
        """Converts a JsonCodelist to a standard codelist."""
        return CategoryScheme(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            items=self.categories,
        )


class JsonCategorySchemes(Struct, frozen=True):
    """SDMX-JSON payload for the list of category schemes."""

    categorisations: Sequence[JsonCategorisation]
    categorySchemes: Sequence[JsonCategoryScheme]
    dataflows: Sequence[JsonDataflowRef]


class JsonCategorySchemeMessage(Struct, frozen=True):
    """SDMX-JSON payload for /categoryscheme queries."""

    data: JsonCategorySchemes

    def __group_flows(self) -> defaultdict[str, list[DataflowRef]]:
        out: defaultdict[str, list[DataflowRef]] = defaultdict(list)
        for c in self.data.categorisations:
            d = find_by_urn(self.data.dataflows, c.source)
            src = c.target[c.target.find(")") + 2 :]
            out[src].append(d.to_model())
        return out

    def __add_flows(
        self, cat: Category, cni: str, cf: Dict[str, list[DataflowRef]]
    ) -> None:
        if cat.categories:
            for c in cat.categories:
                self.__add_flows(c, f"{cni}.{c.id}", cf)
        if cni in cf:
            cat.dataflows = cf[cni]

    def to_model(self) -> CategoryScheme:
        """Returns the requested codelist."""
        cf = self.__group_flows()
        cs = self.data.categorySchemes[0].to_model()
        for c in cs:
            self.__add_flows(c, c.id, cf)
        return cs
