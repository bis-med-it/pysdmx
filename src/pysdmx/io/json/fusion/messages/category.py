"""Collection of Fusion-JSON schemas for categories and category schemes."""

from collections import defaultdict
from typing import Dict, Optional, Sequence, Tuple, Union

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.io.json.fusion.messages.dataflow import FusionDataflow
from pysdmx.model import (
    Agency,
    Category,
    DataflowRef,
    ItemReference,
    Reference,
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
from pysdmx.util import find_by_urn, parse_urn


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

    def __add_flows(
        self, cni: str, cf: Dict[str, list[DF]]
    ) -> Sequence[DataflowRef]:
        if cni in cf:
            return [
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
        else:
            return ()

    def to_model(
        self,
        cat_flows: dict[str, list[DF]],
        cat_other: dict[str, list[Union[ItemReference, Reference]]],
        parent_id: Optional[str] = None,
    ) -> Category:
        """Converts a FusionCode to a standard code."""
        description = self.descriptions[0].value if self.descriptions else None
        cni = f"{parent_id}.{self.id}" if parent_id else self.id
        dataflows = self.__add_flows(cni, cat_flows)
        others = cat_other.get(cni, ())
        return Category(
            id=self.id,
            name=self.names[0].value,
            description=description,
            categories=[
                c.to_model(cat_flows, cat_other, cni) for c in self.items
            ],
            dataflows=dataflows,
            other_references=others,
        )


class FusionCategoryScheme(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a category scheme."""

    id: str
    names: Sequence[FusionString]
    agency: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"
    items: Sequence[FusionCategory] = ()

    def __group_refs(
        self,
        categorisations: Sequence[FusionCategorisation],
        dataflows: Sequence[FusionDataflow],
    ) -> Tuple[
        dict[str, list[DF]], dict[str, list[Union[ItemReference, Reference]]]
    ]:
        flows: defaultdict[str, list[DF]] = defaultdict(list)
        other: defaultdict[str, list[Union[ItemReference, Reference]]] = (
            defaultdict(list)
        )
        for c in categorisations:
            ref = parse_urn(c.structureReference)
            src = c.categoryReference[c.categoryReference.find(")") + 2 :]
            if ref.sdmx_type == "Dataflow":
                d = find_by_urn(dataflows, c.structureReference)
                flows[src].append(d.to_model())
            else:
                other[src].append(ref)
        return (flows, other)

    def to_model(
        self,
        categorisations: Sequence[FusionCategorisation] = (),
        dataflows: Sequence[FusionDataflow] = (),
    ) -> CS:
        """Converts a JsonCodelist to a standard codelist."""
        description = self.descriptions[0].value if self.descriptions else None
        cat_flows, cat_others = self.__group_refs(categorisations, dataflows)
        return CS(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            description=description,
            version=self.version,
            items=[c.to_model(cat_flows, cat_others) for c in self.items],
        )


class FusionCategorySchemeMessage(Struct, frozen=True):
    """Fusion-JSON payload for /categoryscheme queries."""

    CategoryScheme: Sequence[FusionCategoryScheme]
    Categorisation: Sequence[FusionCategorisation] = ()
    Dataflow: Sequence[FusionDataflow] = ()

    def to_model(self) -> CS:
        """Returns the requested category scheme."""
        return self.CategoryScheme[0].to_model(
            self.Categorisation, self.Dataflow
        )


class FusionCategorisationMessage(Struct, frozen=True):
    """Fusion-JSON payload for /categorisation queries."""

    Categorisation: Sequence[FusionCategorisation]

    def to_model(self) -> Sequence[CT]:
        """Returns the requested categorisations."""
        return [c.to_model() for c in self.Categorisation]
