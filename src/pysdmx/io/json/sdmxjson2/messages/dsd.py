"""Collection of SDMX-JSON schemas for SDMX-REST DSD queries."""

from typing import Dict, List, Literal, Optional, Sequence, Tuple, Union

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist, JsonValuelist
from pysdmx.io.json.sdmxjson2.messages.concept import (
    JsonConcept,
    JsonConceptScheme,
)
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    JsonRepresentation,
    MaintainableType,
)
from pysdmx.model import (
    Agency,
    ArrayBoundaries,
    Codelist,
    Component,
    Components,
    Concept,
    DataStructureDefinition,
    DataType,
    Facets,
    ItemReference,
    MetadataComponent,
    Role,
)
from pysdmx.model.dataflow import Group
from pysdmx.util import parse_item_urn


def _find_concept(cs: Sequence[JsonConceptScheme], urn: str) -> JsonConcept:
    r = parse_item_urn(urn)
    f = [
        m
        for m in cs
        if (m.agency == r.agency and m.id == r.id and m.version == r.version)
    ]
    return [c for c in f[0].concepts if c.id == r.item_id][0]


def _get_type(repr_: JsonRepresentation) -> Optional[str]:
    t: Optional[str] = None
    if repr_.enumerationFormat:
        t = repr_.enumerationFormat.dataType
    elif repr_.format:
        t = repr_.format.dataType
    if not t:
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
    dt = DataType(_get_type(local)) if local else None
    facets = local.to_facets() if local else None
    ab = local.to_array_def() if local else None
    return (dt, facets, codes, ab)


def _get_concept_reference(
    component: Union[Component, MetadataComponent],
) -> str:
    if isinstance(component.concept, ItemReference):
        concept = (
            "urn:sdmx:org.sdmx.infomodel.conceptscheme."
            f"{str(component.concept)}"
        )
    elif component.concept.urn:
        concept = component.concept.urn
    else:
        raise errors.Invalid(
            "Missing concept reference",
            (
                "The full reference to the concept must be available "
                "but could not be found. To have the full reference, "
                "either the concept must be an ItemReference or a "
                "concept object with a urn."
            ),
        )
    return concept


def _get_json_representation(
    comp: Union[Component, MetadataComponent],
) -> Optional[JsonRepresentation]:
    enum = comp.local_enum_ref if comp.local_enum_ref else None
    return JsonRepresentation.from_model(
        comp.local_dtype, enum, comp.local_facets, comp.array_def
    )


class JsonGroup(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a group."""

    id: str
    groupDimensions: Sequence[str]


class JsonAttributeRelationship(Struct, frozen=True, omit_defaults=True):
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

    @classmethod
    def from_model(self, rel: str) -> "JsonAttributeRelationship":
        """Converts a pysdmx attribute relationship to an SDMX-JSON one."""
        if rel == "D":
            return JsonAttributeRelationship(dataflow={})
        elif rel == "O":
            return JsonAttributeRelationship(observation={})
        else:
            dims = rel.split(",")
            return JsonAttributeRelationship(dimensions=dims)


class JsonDimension(Struct, frozen=True, omit_defaults=True):
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
        if self.localRepresentation and self.localRepresentation.enumeration:
            local_enum_ref = self.localRepresentation.enumeration
        else:
            local_enum_ref = None
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
            local_enum_ref=local_enum_ref,
        )

    @classmethod
    def from_model(self, dimension: Component) -> "JsonDimension":
        """Converts a pysdmx dimension to an SDMX-JSON one."""
        concept = _get_concept_reference(dimension)
        repr = _get_json_representation(dimension)
        return JsonDimension(
            id=dimension.id,
            conceptIdentity=concept,
            localRepresentation=repr,
        )


class JsonAttribute(Struct, frozen=True, omit_defaults=True):
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
        if self.localRepresentation and self.localRepresentation.enumeration:
            local_enum_ref = self.localRepresentation.enumeration
        else:
            local_enum_ref = None
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
            local_enum_ref=local_enum_ref,
        )

    @classmethod
    def from_model(self, attribute: Component) -> "JsonAttribute":
        """Converts a pysdmx attribute to an SDMX-JSON one."""
        concept = _get_concept_reference(attribute)
        usage = "mandatory" if attribute.required else "optional"
        level = JsonAttributeRelationship.from_model(
            attribute.attachment_level  # type: ignore[arg-type]
        )
        repr = _get_json_representation(attribute)
        return JsonAttribute(
            id=attribute.id,
            conceptIdentity=concept,
            attributeRelationship=level,
            usage=usage,
            localRepresentation=repr,
        )


class JsonMeasure(Struct, frozen=True, omit_defaults=True):
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
        if self.localRepresentation and self.localRepresentation.enumeration:
            local_enum_ref = self.localRepresentation.enumeration
        else:
            local_enum_ref = None
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
            local_enum_ref=local_enum_ref,
        )

    @classmethod
    def from_model(self, measure: Component) -> "JsonMeasure":
        """Converts a pysdmx measure to an SDMX-JSON one."""
        concept = _get_concept_reference(measure)
        usage = "mandatory" if measure.required else "optional"
        repr = _get_json_representation(measure)
        return JsonMeasure(
            id=measure.id,
            conceptIdentity=concept,
            usage=usage,
            localRepresentation=repr,
        )


class JsonAttributes(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of attributes."""

    id: Literal["AttributeDescriptor"] = "AttributeDescriptor"
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

    @classmethod
    def from_model(
        self, attributes: Sequence[Component]
    ) -> Optional["JsonAttributes"]:
        """Converts a pysdmx list of attributes to an SDMX-JSON one."""
        if len(attributes) > 0:
            return JsonAttributes(
                attributes=[JsonAttribute.from_model(a) for a in attributes]
            )
        else:
            return None


class JsonDimensions(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of dimensions."""

    id: Literal["DimensionDescriptor"] = "DimensionDescriptor"
    dimensions: Sequence[JsonDimension] = ()
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

    @classmethod
    def from_model(
        self,
        dimensions: Sequence[Component],
    ) -> "JsonDimensions":
        """Converts a pysdmx list of dimensions to an SDMX-JSON one."""
        td = [d for d in dimensions if d.id == "TIME_PERIOD"]
        ftd = None if len(td) == 0 else JsonDimension.from_model(td[0])
        return JsonDimensions(
            dimensions=[
                JsonDimension.from_model(d)
                for d in dimensions
                if d.id != "TIME_PERIOD"
            ],
            timeDimension=ftd,
        )


class JsonMeasures(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of measures."""

    id: Literal["MeasureDescriptor"] = "MeasureDescriptor"
    measures: Sequence[JsonMeasure] = ()

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[Codelist],
        cons: Dict[str, Sequence[str]],
    ) -> List[Component]:
        """Returns the list of measures."""
        return [m.to_model(cs, cls, cons) for m in self.measures]

    @classmethod
    def from_model(
        self, measures: Sequence[Component]
    ) -> Optional["JsonMeasures"]:
        """Converts a pysdmx list of measures to an SDMX-JSON one."""
        if len(measures) > 0:
            return JsonMeasures(
                measures=[JsonMeasure.from_model(m) for m in measures]
            )
        else:
            return None


class JsonComponents(Struct, frozen=True, omit_defaults=True):
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
    ) -> Tuple[Components, Sequence[Group]]:
        """Returns the components for this DSD."""
        enums = [cl.to_model() for cl in cls]
        enums.extend([vl.to_model() for vl in vls])
        comps = []
        if constraints:
            incl_cubes = [cr for c in constraints for cr in c.cubeRegions if cr.include]
            if len(incl_cubes) == 1:
                cons = incl_cubes[0].to_map()
            else:
                cons = {}
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
        mapped_grps = [
            Group(g.id, dimensions=g.groupDimensions) for g in self.groups
        ]
        return (Components(comps), mapped_grps)

    @classmethod
    def from_model(
        self, components: Components, grps: Optional[Sequence[Group]]
    ) -> "JsonComponents":
        """Converts a pysdmx components list to an SDMX-JSON one."""
        dimensions = JsonDimensions.from_model(components.dimensions)
        attributes = JsonAttributes.from_model(components.attributes)
        measures = JsonMeasures.from_model(components.measures)
        if grps is None:
            groups = []
        else:
            groups = [JsonGroup(g.id, g.dimensions) for g in grps]
        return JsonComponents(dimensions, measures, attributes, groups)


class JsonDataStructure(MaintainableType, frozen=True, omit_defaults=True):
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
        c, grps = self.dataStructureComponents.to_model(  # type: ignore[union-attr]
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
            groups=grps,
        )

    @classmethod
    def from_model(self, dsd: DataStructureDefinition) -> "JsonDataStructure":
        """Converts a pysdmx dsd to an SDMX-JSON one."""
        if not dsd.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON data structures must have a name",
                {"data_structure": dsd.id},
            )

        return JsonDataStructure(
            agency=(
                dsd.agency.id if isinstance(dsd.agency, Agency) else dsd.agency
            ),
            id=dsd.id,
            name=dsd.name,
            version=dsd.version,
            isExternalReference=dsd.is_external_reference,
            validFrom=dsd.valid_from,
            validTo=dsd.valid_to,
            description=dsd.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in dsd.annotations]
            ),
            dataStructureComponents=JsonComponents.from_model(
                dsd.components, dsd.groups
            ),
            evolvingStructure=dsd.evolving_structure,
        )


class JsonDataStructures(Struct, frozen=True, omit_defaults=True):
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


class JsonDataStructuresMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /datastructure queries."""

    data: JsonDataStructures

    def to_model(self) -> Sequence[DataStructureDefinition]:
        """Returns the requested data structures."""
        return self.data.to_model()
