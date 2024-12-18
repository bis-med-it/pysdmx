"""Collection of Fusion-JSON schemas for SDMX-REST schema queries."""

from typing import Dict, List, Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx.errors import InternalError
from pysdmx.io.json.fusion.messages.code import FusionCodelist
from pysdmx.io.json.fusion.messages.concept import (
    FusionConcept,
    FusionConceptScheme,
)
from pysdmx.io.json.fusion.messages.constraint import FusionContentConstraint
from pysdmx.io.json.fusion.messages.core import (
    FusionRepresentation,
    FusionString,
)
from pysdmx.model import (
    ArrayBoundaries,
    Codelist,
    Component,
    Components,
    DataType,
    Facets,
    Role,
)
from pysdmx.util import parse_item_urn


def _find_concept(
    cs: Sequence[FusionConceptScheme],
    urn: str,
) -> FusionConcept:
    r = parse_item_urn(urn)
    f = [
        m
        for m in cs
        if (m.agency == r.agency and m.id == r.id and m.version == r.version)
    ]
    return [c for c in f[0].items if c.id == r.item_id][0]


def _get_representation(
    id_: str,
    r: Optional[FusionRepresentation],
    cls: Sequence[FusionCodelist],
    cons: Dict[str, Sequence[str]],
) -> Tuple[
    Optional[DataType],
    Optional[Facets],
    Optional[Codelist],
    Optional[ArrayBoundaries],
]:
    ab = r.to_array_def() if r else None
    dt = DataType(r.textFormat.textType) if r and r.textFormat else None
    facets = r.to_facets() if r else None
    codes = r.to_enumeration(cls, cons.get(id_, [])) if r else None
    return (dt, facets, codes, ab)


class FusionGroup(Struct, frozen=True):
    """Fusion-JSON payload for a group."""

    id: str
    dimensionReferences: Sequence[str]


class FusionAttribute(Struct, frozen=True):
    """Fusion-JSON payload for an attribute."""

    id: str
    concept: str
    mandatory: bool
    attachmentLevel: str
    representation: Optional[FusionRepresentation] = None
    attachmentGroup: Optional[str] = None
    dimensionReferences: Optional[Sequence[str]] = None
    measureReferences: Optional[Sequence[str]] = None

    def __derive_level(self, groups: Sequence[FusionGroup]) -> str:
        if self.attachmentLevel == "OBSERVATION":
            return "O"
        elif self.attachmentLevel == "DATA_SET":
            return "D"
        elif self.attachmentLevel == "GROUP":
            grp = [g for g in groups if g.id == self.attachmentGroup]
            return ",".join(grp[0].dimensionReferences)
        elif self.dimensionReferences:
            return ",".join(self.dimensionReferences)
        else:
            raise InternalError(
                "Invalid metadata",
                (
                    "Could not infer attribute attachment level. "
                    f"The attribute is {self}"
                ),
            )

    def to_model(
        self,
        cs: Sequence[FusionConceptScheme],
        cls: Sequence[FusionCodelist],
        cons: Dict[str, Sequence[str]],
        groups: Sequence[FusionGroup],
    ) -> Component:
        """Returns an attribute."""
        c = _find_concept(cs, self.concept)
        dt, facets, codes, ab = _get_representation(
            self.id, self.representation, cls, cons
        )
        lvl = self.__derive_level(groups)
        if c.descriptions:
            desc = c.descriptions[0].value
        else:
            desc = None
        return Component(
            id=self.id,
            required=self.mandatory,
            role=Role.ATTRIBUTE,
            concept=c.to_model(cls),
            local_dtype=dt,
            local_facets=facets,
            name=c.names[0].value,
            description=desc,
            local_codes=codes,
            attachment_level=lvl,
            array_def=ab,
        )


class FusionAttributes(Struct, frozen=True):
    """Fusion-JSON payload for the list of attributes."""

    attributes: Sequence[FusionAttribute]

    def to_model(
        self,
        cs: Sequence[FusionConceptScheme],
        cls: Sequence[FusionCodelist],
        cons: Dict[str, Sequence[str]],
        groups: Sequence[FusionGroup],
    ) -> List[Component]:
        """Returns the list of attributes."""
        return [d.to_model(cs, cls, cons, groups) for d in self.attributes]


class FusionDimension(Struct, frozen=True):
    """Fusion-JSON payload for a dimension."""

    id: str
    concept: str
    representation: Optional[FusionRepresentation] = None

    def to_model(
        self,
        cs: Sequence[FusionConceptScheme],
        cls: Sequence[FusionCodelist],
        cons: Dict[str, Sequence[str]],
    ) -> Component:
        """Returns a dimension."""
        c = _find_concept(cs, self.concept)
        dt, facets, codes, ab = _get_representation(
            self.id, self.representation, cls, cons
        )
        if c.descriptions:
            desc = c.descriptions[0].value
        else:
            desc = None
        return Component(
            id=self.id,
            required=True,
            role=Role.DIMENSION,
            concept=c.to_model(cls),
            local_dtype=dt,
            local_facets=facets,
            name=c.names[0].value,
            description=desc,
            local_codes=codes,
            array_def=ab,
        )


class FusionDimensions(Struct, frozen=True):
    """Fusion-JSON payload for the list of dimensions."""

    dimensions: Sequence[FusionDimension]

    def to_model(
        self,
        cs: Sequence[FusionConceptScheme],
        cls: Sequence[FusionCodelist],
        cons: Dict[str, Sequence[str]],
    ) -> List[Component]:
        """Returns the list of dimensions."""
        return [d.to_model(cs, cls, cons) for d in self.dimensions]


class FusionMeasure(Struct, frozen=True):
    """Fusion-JSON payload for a measure."""

    id: str
    concept: str
    mandatory: bool
    representation: Optional[FusionRepresentation] = None

    def to_model(
        self,
        cs: Sequence[FusionConceptScheme],
        cls: Sequence[FusionCodelist],
        cons: Dict[str, Sequence[str]],
    ) -> Component:
        """Returns a measure."""
        c = _find_concept(cs, self.concept)
        dt, facets, codes, ab = _get_representation(
            self.id, self.representation, cls, cons
        )
        if c.descriptions:
            desc = c.descriptions[0].value
        else:
            desc = None
        return Component(
            id=self.id,
            required=self.mandatory,
            role=Role.MEASURE,
            concept=c.to_model(cls),
            local_dtype=dt,
            local_facets=facets,
            name=c.names[0].value,
            description=desc,
            local_codes=codes,
            array_def=ab,
        )


class FusionDataStructure(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a DSD."""

    id: str
    names: Sequence[FusionString]
    agency: str
    dimensionList: FusionDimensions
    measures: Sequence[FusionMeasure] = ()
    attributeList: Optional[FusionAttributes] = None
    groups: Sequence[FusionGroup] = ()
    description: Optional[Sequence[FusionString]] = None
    version: str = "1.0"

    def get_components(
        self,
        cs: Sequence[FusionConceptScheme],
        cls: Sequence[FusionCodelist],
        constraints: Sequence[FusionContentConstraint],
    ) -> Components:
        """Returns the schema for this DSD."""
        comps = []
        if constraints:
            cons = constraints[0].to_map()
        else:
            cons = {}
        comps.extend(self.dimensionList.to_model(cs, cls, cons))
        if self.measures:
            comps.extend([m.to_model(cs, cls, cons) for m in self.measures])
        if self.attributeList:
            comps.extend(
                self.attributeList.to_model(
                    cs,
                    cls,
                    cons,
                    self.groups,
                )
            )
        return Components(comps)
