"""Collection of Fusion-JSON schemas for categories and category schemes."""

from collections import defaultdict
from typing import Dict, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.io.json.fusion.messages.dataflow import FusionDataflowRef
from pysdmx.model import Category, CategoryScheme as CS, DataflowRef
from pysdmx.util import find_by_urn


class FusionCategorisation(Struct, frozen=True):
    """Fusion-JSON payload for a categorisation."""

    categoryReference: str
    structureReference: str


class FusionCategory(Struct, frozen=True):
    """Fusion-JSON payload for a category."""

    id: str
    names: Sequence[FusionString]
    descriptions: Optional[Sequence[FusionString]] = None
    items: Sequence["FusionCategory"] = ()

    def to_model(self) -> Category:
        """Converts a FusionCode to a standard code."""
        description = self.descriptions[0].value if self.descriptions else None
        return Category(
            id=self.id,
            name=self.names[0].value,
            description=description,
            categories=[c.to_model() for c in self.items],
        )


class FusionCategoryScheme(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a category scheme."""

    id: str
    names: Sequence[FusionString]
    agency: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"
    items: Sequence[FusionCategory] = ()

    def to_model(self) -> CS:
        """Converts a JsonCodelist to a standard codelist."""
        description = self.descriptions[0].value if self.descriptions else None
        return CS(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            description=description,
            version=self.version,
            items=[c.to_model() for c in self.items],
        )


class FusionCategorySchemeMessage(Struct, frozen=True):
    """Fusion-JSON payload for /categoryscheme queries."""

    Categorisation: Sequence[FusionCategorisation]
    CategoryScheme: Sequence[FusionCategoryScheme]
    Dataflow: Sequence[FusionDataflowRef]

    def __group_flows(self) -> defaultdict[str, list[DataflowRef]]:
        out: defaultdict[str, list[DataflowRef]] = defaultdict(list)
        for c in self.Categorisation:
            d = find_by_urn(self.Dataflow, c.structureReference)
            src = c.categoryReference[c.categoryReference.find(")") + 2 :]
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

    def to_model(self) -> CS:
        """Returns the requested codelist."""
        cf = self.__group_flows()
        cs = self.CategoryScheme[0].to_model()
        for c in cs:
            self.__add_flows(c, c.id, cf)
        return cs
