"""Collection of SDMX-JSON schemas for SDMX-REST schema queries."""

from typing import Dict, List, Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx.fmr.sdmx.concept import JsonConcept, JsonConceptScheme
from pysdmx.fmr.sdmx.constraint import JsonContentConstraint
from pysdmx.fmr.sdmx.core import JsonRepresentation
from pysdmx.model import (
    ArrayBoundaries,
    Code,
    Codelist,
    Component,
    Components,
    DataType,
    Facets,
    Role,
)
from pysdmx.util import parse_item_urn


def _find_concept(cs: Sequence[JsonConceptScheme], urn: str) -> JsonConcept:
    r = parse_item_urn(urn)
    f = [
        m
        for m in cs
        if (m.agency == r.agency and m.id == r.id and m.version == r.version)
    ]
    return [c for c in f[0].concepts if c.id == r.item_id][0]


def __get_type(repr_: JsonRepresentation) -> str:
    if repr_.enumerationFormat:
        t = repr_.enumerationFormat.textType
    elif repr_.format:
        t = repr_.format.textType
    else:
        t = "String"
    return t


def _get_representation(
    id_: str,
    local: Optional[JsonRepresentation],
    core: Optional[JsonRepresentation],
    cls: Sequence[Codelist],
    cons: Dict[str, Sequence[str]],
) -> Tuple[
    DataType,
    Optional[Facets],
    Sequence[Code],
    Optional[str],
    Optional[ArrayBoundaries],
]:
    valid = cons.get(id_, [])
    codes: Sequence[Code] = []
    dt = DataType.STRING
    facets = None
    cl_ref = None
    ab = None
    if local:
        dt = DataType(__get_type(local))
        facets = local.to_facets()
        codes = local.to_enumeration(cls, valid)
        cl_ref = local.enumeration
        ab = local.to_array_def()
    elif core:
        dt = DataType(__get_type(core))
        facets = core.to_facets()
        codes = core.to_enumeration(cls, valid)
        cl_ref = core.enumeration
        ab = core.to_array_def()
    return (dt, facets, codes, cl_ref, ab)


class JsonGroup(Struct, frozen=True):
    """SDMX-JSON payload for a group."""

    id: str
    groupDimensions: Sequence[str]


class JsonAttributeRelationship(Struct, frozen=True):
    """SDMX-JSON payload for an attribute relationship."""

    dimensions: Optional[Sequence[str]] = None
    group: Optional[str] = None

    def to_model(
        self, groups: Sequence[JsonGroup], measures: Optional[Sequence[str]]
    ) -> str:
        """Returns the attachment level."""
        if measures:
            return "O"
        elif self.dimensions:
            return ",".join(self.dimensions)
        elif self.group:
            grp = [g for g in groups if g.id == self.group]
            return ",".join(grp[0].groupDimensions)
        else:
            return "D"


class JsonDimension(Struct, frozen=True):
    """SDMX-JSON payload for a component."""

    id: str
    conceptIdentity: str
    localRepresentation: Optional[JsonRepresentation] = None

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
    ) -> Component:
        """Returns a component."""
        c = _find_concept(cs, self.conceptIdentity)
        dt, facets, codes, cl_ref, ab = _get_representation(
            self.id, self.localRepresentation, c.coreRepresentation, cls, cons
        )
        return Component(
            self.id,
            True,
            Role.DIMENSION,
            dt,
            facets,
            c.name,
            c.description,
            codes=codes,
            enum_ref=cl_ref,
            array_def=ab,
        )


class JsonAttribute(Struct, frozen=True):
    """SDMX-JSON payload for an attribute."""

    id: str
    conceptIdentity: str
    attributeRelationship: JsonAttributeRelationship
    usage: str = "optional"
    measureRelationship: Optional[Sequence[str]] = None
    localRepresentation: Optional[JsonRepresentation] = None

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
        groups: Sequence[JsonGroup],
    ) -> Component:
        """Returns a component."""
        c = _find_concept(cs, self.conceptIdentity)
        dt, facets, codes, cl_ref, ab = _get_representation(
            self.id, self.localRepresentation, c.coreRepresentation, cls, cons
        )
        req = self.usage != "optional"
        lvl = self.attributeRelationship.to_model(
            groups,
            self.measureRelationship,
        )
        return Component(
            self.id,
            req,
            Role.ATTRIBUTE,
            dt,
            facets,
            c.name,
            c.description,
            codes=codes,
            attachment_level=lvl,
            enum_ref=cl_ref,
            array_def=ab,
        )


class JsonMeasure(Struct, frozen=True):
    """SDMX-JSON payload for a measure."""

    id: str
    conceptIdentity: str
    usage: str = "optional"
    localRepresentation: Optional[JsonRepresentation] = None

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
    ) -> Component:
        """Returns a component."""
        c = _find_concept(cs, self.conceptIdentity)
        dt, facets, codes, cl_ref, ab = _get_representation(
            self.id, self.localRepresentation, c.coreRepresentation, cls, cons
        )
        req = self.usage != "optional"
        return Component(
            self.id,
            req,
            Role.MEASURE,
            dt,
            facets,
            c.name,
            c.description,
            codes=codes,
            enum_ref=cl_ref,
            array_def=ab,
        )


class JsonAttributes(Struct, frozen=True):
    """SDMX-JSON payload for the list of attributes."""

    attributes: Sequence[JsonAttribute] = ()

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
        groups: Sequence[JsonGroup],
    ) -> List[Component]:
        """Returns the list of attributes."""
        return [d.to_model(cs, cls, cons, groups) for d in self.attributes]


class JsonDimensions(Struct, frozen=True):
    """SDMX-JSON payload for the list of dimensions."""

    dimensions: Sequence[JsonDimension]
    timeDimensions: Sequence[JsonDimension] = ()

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
    ) -> List[Component]:
        """Returns the list of dimensions."""
        c = []
        c.extend([d.to_model(cs, cls, cons) for d in self.dimensions])
        c.extend([d.to_model(cs, cls, cons) for d in self.timeDimensions])
        return c


class JsonMeasures(Struct, frozen=True):
    """SDMX-JSON payload for the list of measures."""

    measures: Sequence[JsonMeasure]

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
    ) -> List[Component]:
        """Returns the list of measures."""
        return [m.to_model(cs, cls, cons) for m in self.measures]


class JsonComponents(Struct, frozen=True):
    """SDMX-JSON payload for the list of DSD components."""

    dimensionList: JsonDimensions
    measureList: Optional[JsonMeasures] = None
    attributeList: Optional[JsonAttributes] = None
    groups: Sequence[JsonGroup] = ()

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        constraints: Sequence[JsonContentConstraint],
    ) -> Components:
        """Returns the schema for this DSD."""
        comps = []
        if constraints:
            cons = constraints[0].cubeRegions[0].to_map()
        else:
            cons = {}
        comps.extend(self.dimensionList.to_model(cs, cls, cons))
        if self.measureList:
            comps.extend(self.measureList.to_model(cs, cls, cons))
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


class JsonDataStructure(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a DSD."""

    id: str
    name: str
    agency: str
    dataStructureComponents: JsonComponents
    description: Optional[str] = None
    version: str = "1.0"
