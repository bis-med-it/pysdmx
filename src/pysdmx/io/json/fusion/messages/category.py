"""Collection of Fusion-JSON schemas for categories and category schemes."""

from collections import defaultdict
from typing import Dict, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.io.json.fusion.messages.dataflow import FusionDataflow
from pysdmx.model import (
    Agency,
    Category,
    DataflowRef,
)
from pysdmx.model import (
    Categorisation as CT,
)
from pysdmx.model import (
    CategoryScheme as CS,
)
from pysdmx.model import (
    Dataflow as DF,
)
from pysdmx.util import find_by_urn


class FusionCategorisation(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a categorisation."""

    id: str
    names: Sequence[FusionString]
    agency: str
    categoryReference: str
    structureReference: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"

    def to_model(self) -> CT:
        """Converts a JsonCategorisation to a standard categorisation."""
        description = self.descriptions[0].value if self.descriptions else None
        return CT(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            description=description,
            version=self.version,
            source=self.structureReference,
            target=self.categoryReference,
        )


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

    CategoryScheme: Sequence[FusionCategoryScheme]
    Categorisation: Sequence[FusionCategorisation] = ()
    Dataflow: Sequence[FusionDataflow] = ()

    def __group_flows(self) -> defaultdict[str, list[DF]]:
        out: defaultdict[str, list[DF]] = defaultdict(list)
        for c in self.Categorisation:
            d = find_by_urn(self.Dataflow, c.structureReference)
            src = c.categoryReference[c.categoryReference.find(")") + 2 :]
            out[src].append(d.to_model())
        return out

    def __add_flows(
        self, cat: Category, cni: str, cf: Dict[str, list[DF]]
    ) -> None:
        if cat.categories:
            for c in cat.categories:
                self.__add_flows(c, f"{cni}.{c.id}", cf)
        if cni in cf:
            dfrefs = [
                DataflowRef(
                    (
                        df.agency.id
                        if isinstance(df.agency, Agency)
                        else df.agency
                    ),
                    df.id,
                    df.version,
                    df.name,
                )
                for df in cf[cni]
            ]
            cat.dataflows = dfrefs

    def to_model(self) -> CS:
        """Returns the requested category scheme."""
        cf = self.__group_flows()
        cs = self.CategoryScheme[0].to_model()
        for c in cs:
            self.__add_flows(c, c.id, cf)
        return cs


class FusionCategorisationMessage(Struct, frozen=True):
    """Fusion-JSON payload for /categorisation queries."""

    Categorisation: Sequence[FusionCategorisation]

    def to_model(self) -> Sequence[CT]:
        """Returns the requested categorisations."""
        return [c.to_model() for c in self.Categorisation]
