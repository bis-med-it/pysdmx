"""Collection of SDMX-JSON schemas for categories and category schemes."""

from collections import defaultdict
from datetime import datetime
from typing import Dict, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflow
from pysdmx.model import (
    Agency,
    Categorisation,
    Category,
    CategoryScheme,
    Dataflow,
    DataflowRef,
)
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

    def to_model(self) -> Categorisation:
        """Converts a JsonCategorisation to a standard categorisation."""
        return Categorisation(
            id=self.id,
            agency=self.agency,
            version=self.version,
            source=self.source,
            target=self.target,
            name=self.name,
            description=self.description,
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )


class JsonCategory(Struct, frozen=True):
    """SDMX-JSON payload for a category."""

    id: str  # type: ignore[misc, unused-ignore]
    name: Optional[str] = None
    description: Optional[str] = None
    categories: Sequence["JsonCategory"] = ()

    def to_model(self) -> Category:
        """Converts a FusionCode to a standard code."""
        return Category(
            id=self.id,
            name=self.name,
            description=self.description,
            categories=[c.to_model() for c in self.categories],
        )


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
    categories: Sequence[JsonCategory] = ()

    def to_model(self) -> CategoryScheme:
        """Converts a JsonCodelist to a standard codelist."""
        return CategoryScheme(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            items=[c.to_model() for c in self.categories],
        )


class JsonCategorySchemes(Struct, frozen=True):
    """SDMX-JSON payload for the list of category schemes."""

    categorySchemes: Sequence[JsonCategoryScheme]
    categorisations: Sequence[JsonCategorisation] = ()
    dataflows: Sequence[JsonDataflow] = ()


class JsonCategorySchemeMessage(Struct, frozen=True):
    """SDMX-JSON payload for /categoryscheme queries."""

    data: JsonCategorySchemes

    def __group_flows(self) -> defaultdict[str, list[Dataflow]]:
        out: defaultdict[str, list[Dataflow]] = defaultdict(list)
        for c in self.data.categorisations:
            d = find_by_urn(self.data.dataflows, c.source)
            src = c.target[c.target.find(")") + 2 :]
            out[src].append(d.to_model())
        return out

    def __add_flows(
        self, cat: Category, cni: str, cf: Dict[str, list[Dataflow]]
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

    def to_model(self) -> CategoryScheme:
        """Returns the requested codelist."""
        cf = self.__group_flows()
        cs = self.data.categorySchemes[0].to_model()
        for c in cs:
            self.__add_flows(c, c.id, cf)
        return cs


class JsonCategorisations(Struct, frozen=True):
    """SDMX-JSON payload for the list of categorisations."""

    categorisations: Sequence[JsonCategorisation]


class JsonCategorisationMessage(Struct, frozen=True):
    """SDMX-JSON payload for /categorisation queries."""

    data: JsonCategorisations

    def to_model(self) -> Sequence[Categorisation]:
        """Returns the requested categorisations."""
        return [cat.to_model() for cat in self.data.categorisations]
