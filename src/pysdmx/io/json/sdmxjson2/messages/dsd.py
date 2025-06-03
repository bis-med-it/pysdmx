"""Collection of SDMX-JSON schemas for SDMX-REST schema queries."""

from typing import Dict, List, Optional, Sequence, Tuple

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist, JsonValuelist
from pysdmx.io.json.sdmxjson2.messages.concept import (
    JsonConcept,
    JsonConceptScheme,
)
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonRepresentation,
    MaintainableType,
)
from pysdmx.model import (
    ArrayBoundaries,
    Codelist,
    Component,
    Components,
    Concept,
    DataStructureDefinition,
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
        t = repr_.enumerationFormat.dataType
    elif repr_.format:
        t = repr_.format.dataType
    else:
        t = "String"
    return t


def _get_representation(
    id_: str,
    local: Optional[JsonRepresentation],
    cls: Sequence[Codelist],
    cons: Dict[str, Sequence[str]],
) -> Tuple[
    Optional[DataType],
    Optional[Facets],
    Optional[Codelist],
    Optional[ArrayBoundaries],
]:
    valid = cons.get(id_, [])
    codes = local.to_enumeration(cls, valid) if local else None
    dt = DataType(__get_type(local)) if local else None
    facets = local.to_facets() if local else None
    ab = local.to_array_def() if local else None
    return (dt, facets, codes, ab)


class JsonGroup(Struct, frozen=True):
    """SDMX-JSON payload for a group."""

    id: str
    groupDimensions: Sequence[str]


class JsonAttributeRelationship(Struct, frozen=True):
    """SDMX-JSON payload for an attribute relationship."""

    dataflow: Optional[Dict] = None  # type: ignore[type-arg]
    dimensions: Optional[Sequence[str]] = None
    group: Optional[str] = None
    observation: Optional[Dict] = None  # type: ignore[type-arg]

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
    position: Optional[int] = None
    conceptRoles: Optional[Sequence[str]] = None
    localRepresentation: Optional[JsonRepresentation] = None

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
    ) -> Component:
        """Returns a component."""
        c = (
            _find_concept(cs, self.conceptIdentity).to_model(cls)
            if cs
            else parse_item_urn(self.conceptIdentity)
        )
        name = c.name if isinstance(c, Concept) else None
        desc = c.description if isinstance(c, Concept) else None
        dt, facets, codes, ab = _get_representation(
            self.id, self.localRepresentation, cls, cons
        )
        return Component(
            id=self.id,
            required=True,
            role=Role.DIMENSION,
            concept=c,
            local_dtype=dt,
            local_facets=facets,
            name=name,
            description=desc,
            local_codes=codes,
            array_def=ab,
        )


class JsonAttribute(Struct, frozen=True):
    """SDMX-JSON payload for an attribute."""

    id: str
    conceptIdentity: str
    attributeRelationship: JsonAttributeRelationship
    conceptRoles: Optional[Sequence[str]] = None
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
        c = (
            _find_concept(cs, self.conceptIdentity).to_model(cls)
            if cs
            else parse_item_urn(self.conceptIdentity)
        )
        name = c.name if isinstance(c, Concept) else None
        desc = c.description if isinstance(c, Concept) else None
        dt, facets, codes, ab = _get_representation(
            self.id, self.localRepresentation, cls, cons
        )
        req = self.usage != "optional"
        lvl = self.attributeRelationship.to_model(
            groups,
            self.measureRelationship,
        )
        return Component(
            id=self.id,
            required=req,
            role=Role.ATTRIBUTE,
            concept=c,
            local_dtype=dt,
            local_facets=facets,
            name=name,
            description=desc,
            local_codes=codes,
            attachment_level=lvl,
            array_def=ab,
        )


class JsonMeasure(Struct, frozen=True):
    """SDMX-JSON payload for a measure."""

    id: str
    conceptIdentity: str
    conceptRoles: Optional[Sequence[str]] = None
    usage: str = "optional"
    localRepresentation: Optional[JsonRepresentation] = None

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
    ) -> Component:
        """Returns a component."""
        c = (
            _find_concept(cs, self.conceptIdentity).to_model(cls)
            if cs
            else parse_item_urn(self.conceptIdentity)
        )
        name = c.name if isinstance(c, Concept) else None
        desc = c.description if isinstance(c, Concept) else None
        dt, facets, codes, ab = _get_representation(
            self.id, self.localRepresentation, cls, cons
        )
        req = self.usage != "optional"
        return Component(
            id=self.id,
            required=req,
            role=Role.MEASURE,
            concept=c,
            local_dtype=dt,
            local_facets=facets,
            name=name,
            description=desc,
            local_codes=codes,
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
        return [a.to_model(cs, cls, cons, groups) for a in self.attributes]


class JsonDimensions(Struct, frozen=True):
    """SDMX-JSON payload for the list of dimensions."""

    dimensions: Sequence[JsonDimension]
    timeDimension: Optional[JsonDimension] = None

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
    ) -> List[Component]:
        """Returns the list of dimensions."""
        dims = []
        dims.extend([d.to_model(cs, cls, cons) for d in self.dimensions])
        if self.timeDimension:
            dims.append(self.timeDimension.to_model(cs, cls, cons))
        return dims


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
        cls: Sequence[JsonCodelist],
        vls: Sequence[JsonValuelist],
        constraints: Sequence[JsonDataConstraint],
    ) -> Components:
        """Returns the components for this DSD."""
        enums = [cl.to_model() for cl in cls]
        enums.extend([vl.to_model() for vl in vls])
        comps = []
        if constraints and constraints[0].cubeRegions:
            cons = constraints[0].cubeRegions[0].to_map()
        else:
            cons = {}
        comps.extend(self.dimensionList.to_model(cs, enums, cons))
        if self.measureList:
            comps.extend(self.measureList.to_model(cs, enums, cons))
        if self.attributeList:
            comps.extend(
                self.attributeList.to_model(
                    cs,
                    enums,
                    cons,
                    self.groups,
                )
            )
        return Components(comps)


class JsonDataStructure(MaintainableType, frozen=True):
    """SDMX-JSON payload for a DSD."""

    dataStructureComponents: Optional[JsonComponents] = None
    evolvingStructure: bool = False

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[JsonCodelist],
        vls: Sequence[JsonValuelist],
        constraints: Sequence[JsonDataConstraint],
    ) -> DataStructureDefinition:
        """Map to pysdmx model class."""
        c = self.dataStructureComponents.to_model(  # type: ignore[union-attr]
            cs,
            cls,
            vls,
            constraints,
        )
        return DataStructureDefinition(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            components=c,
            evolving_structure=self.evolvingStructure,
        )


class JsonDataStructures(Struct, frozen=True):
    """SDMX-JSON payload for data structures."""

    dataStructures: Sequence[JsonDataStructure]
    conceptSchemes: Sequence[JsonConceptScheme] = ()
    valuelists: Sequence[JsonValuelist] = ()
    codelists: Sequence[JsonCodelist] = ()
    contentConstraints: Sequence[JsonDataConstraint] = ()

    def to_model(self) -> Sequence[DataStructureDefinition]:
        """Returns the requested dsds."""
        return [
            dsd.to_model(
                self.conceptSchemes,
                self.codelists,
                self.valuelists,
                self.contentConstraints,
            )
            for dsd in self.dataStructures
        ]


class JsonDataStructuresMessage(Struct, frozen=True):
    """SDMX-JSON payload for /datastructure queries."""

    data: JsonDataStructures

    def to_model(self) -> Sequence[DataStructureDefinition]:
        """Returns the requested data structures."""
        return self.data.to_model()
