"""Collection of Fusion-JSON schemas for SDMX-REST schema queries."""
from typing import Dict, List, Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx.errors import ServiceError
from pysdmx.fmr.fusion.code import FusionCodelist
from pysdmx.fmr.fusion.concept import FusionConcept, FusionConceptScheme
from pysdmx.fmr.fusion.constraint import FusionContentConstraint
from pysdmx.fmr.fusion.core import FusionRepresentation, FusionString
from pysdmx.model import (
    ArrayBoundaries,
    Code,
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
    repr_: Optional[FusionRepresentation],
    cls: Sequence[FusionCodelist],
    cons: Dict[str, Sequence[str]],
    c: Optional[FusionConcept],
) -> Tuple[
    DataType,
    Optional[Facets],
    Sequence[Code],
    Optional[str],
    Optional[ArrayBoundaries],
]:
    valid = cons.get(id_, [])
    codes: Sequence[Code] = []
    cl_ref = None
    ab = None
    dt = DataType.STRING
    facets = None
    codes = []
    if repr_:
        r = repr_
    elif c and c.representation:
        r = c.representation
    else:
        r = None
    if r:
        if r.textFormat:
            dt = DataType(r.textFormat.textType)
        facets = r.to_facets()
        codes = r.to_enumeration(cls, valid)
        cl_ref = r.representation
        ab = r.to_array_def()
    return (dt, facets, codes, cl_ref, ab)


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
            raise ServiceError(
                500,
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
        dt, facets, codes, cl_ref, ab = _get_representation(
            self.id, self.representation, cls, cons, c
        )
        lvl = self.__derive_level(groups)
        if c.descriptions:
            desc = c.descriptions[0].value
        else:
            desc = None
        return Component(
            self.id,
            self.mandatory,
            Role.ATTRIBUTE,
            dt,
            facets,
            c.names[0].value,
            desc,
            codes=codes,
            attachment_level=lvl,
            enum_ref=cl_ref,
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
        dt, facets, codes, cl_ref, ab = _get_representation(
            self.id, self.representation, cls, cons, c
        )
        if c.descriptions:
            desc = c.descriptions[0].value
        else:
            desc = None
        return Component(
            self.id,
            True,
            Role.DIMENSION,
            dt,
            facets,
            c.names[0].value,
            desc,
            codes=codes,
            enum_ref=cl_ref,
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
        dt, facets, codes, cl_ref, ab = _get_representation(
            self.id, self.representation, cls, cons, c
        )
        if c.descriptions:
            desc = c.descriptions[0].value
        else:
            desc = None
        return Component(
            self.id,
            self.mandatory,
            Role.MEASURE,
            dt,
            facets,
            c.names[0].value,
            desc,
            codes=codes,
            enum_ref=cl_ref,
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
