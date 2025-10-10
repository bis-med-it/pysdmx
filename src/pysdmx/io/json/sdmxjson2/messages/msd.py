"""Collection of SDMX-JSON schemas for SDMX-REST MSD queries."""

from typing import List, Literal, Optional, Sequence, Union

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist, JsonValuelist
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConceptScheme
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.io.json.sdmxjson2.messages.core import (
    JsonAnnotation,
    JsonRepresentation,
    MaintainableType,
)
from pysdmx.io.json.sdmxjson2.messages.dsd import (
    _find_concept,
    _get_concept_reference,
    _get_representation,
    _get_json_representation,
)
from pysdmx.model import (
    Agency,
    ArrayBoundaries,
    Codelist,
    Component,
    MetadataComponent,
    MetadataStructure,
)
from pysdmx.util import parse_item_urn


class JsonMetadataAttribute(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for an attribute."""

    id: str
    conceptIdentity: str
    minOccurs: int
    maxOccurs: Union[int, Literal["unbounded"]]
    isPresentational: bool
    localRepresentation: Optional[JsonRepresentation] = None

    def to_model(
        self, cs: Sequence[JsonConceptScheme], cls: Sequence[Codelist]
    ) -> MetadataComponent:
        """Returns a metadata component."""
        c = (
            _find_concept(cs, self.conceptIdentity).to_model(cls)
            if cs
            else parse_item_urn(self.conceptIdentity)
        )
        dt, facets, codes, _ = _get_representation(
            self.id, self.localRepresentation, cls, {}
        )

        if self.localRepresentation and self.localRepresentation.enumeration:
            local_enum_ref = self.localRepresentation.enumeration
        else:
            local_enum_ref = None

        if self.maxOccurs == "unbounded":
            ab = ArrayBoundaries(self.minOccurs)
        elif self.maxOccurs > 1:
            ab = ArrayBoundaries(self.minOccurs, self.maxOccurs)
        else:
            ab = None

        return MetadataComponent(
            id=self.id,
            is_presentational=self.isPresentational,
            concept=c,
            local_dtype=dt,
            local_facets=facets,
            local_codes=codes,
            array_def=ab,
            local_enum_ref=local_enum_ref,
            components=(),
        )

    @classmethod
    def from_model(self, cmp: MetadataComponent) -> "JsonMetadataAttribute":
        """Converts a pysdmx metadata attribute to an SDMX-JSON one."""
        concept = _get_concept_reference(cmp)
        repr = _get_json_representation(cmp)

        min_occurs = cmp.array_def.min_size if cmp.array_def else 0
        if cmp.array_def is None or cmp.array_def.max_size is None:
            max_occurs = "unbounded"
        else:
            max_occurs = cmp.array_def.max_size

        return JsonMetadataAttribute(
            id=cmp.id,
            conceptIdentity=concept,
            localRepresentation=repr,
            minOccurs=min_occurs,
            maxOccurs=max_occurs,
            isPresentational=cmp.is_presentational,
        )


class JsonMetadataAttributes(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of metadata attributes."""

    id: Literal["MetadataAttributeDescriptor"] = "MetadataAttributeDescriptor"
    metadataAttributes: Sequence[JsonMetadataAttribute] = ()

    def to_model(
        self, cs: Sequence[JsonConceptScheme], cls: Sequence[Codelist]
    ) -> List[Component]:
        """Returns the list of metadata attributes."""
        return [a.to_model(cs, cls) for a in self.metadataAttributes]

    @classmethod
    def from_model(
        self, attributes: Sequence[Component]
    ) -> "JsonMetadataAttributes":
        """Converts a pysdmx list of metadata attributes to SDMX-JSON."""
        return JsonMetadataAttributes(
            metadataAttributes=[
                JsonMetadataAttribute.from_model(a) for a in attributes
            ]
        )


class JsonMetadataComponents(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of DSD components."""

    metadataAttributeList: Optional[JsonMetadataAttributes] = None

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[JsonCodelist],
        vls: Sequence[JsonValuelist],
    ) -> Sequence[MetadataComponent]:
        """Returns the components for this DSD."""
        enums = [cl.to_model() for cl in cls]
        enums.extend([vl.to_model() for vl in vls])
        comps = (
            self.metadataAttributeList.to_model(cs, enums)
            if self.metadataAttributeList
            else []
        )
        return comps

    @classmethod
    def from_model(
        self, components: Sequence[MetadataComponent]
    ) -> "JsonMetadataComponents":
        """Converts a pysdmx components list to an SDMX-JSON one."""
        attributes = JsonMetadataAttributes.from_model(components)
        return JsonMetadataComponents(metadataAttributeList=attributes)


class JsonMetadataStructure(MaintainableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a DSD."""

    metadataStructureComponents: Optional[JsonMetadataComponents] = None

    def to_model(
        self,
        cs: Sequence[JsonConceptScheme],
        cls: Sequence[JsonCodelist],
        vls: Sequence[JsonValuelist],
    ) -> MetadataStructure:
        """Map to pysdmx model class."""
        c = self.metadataStructureComponents.to_model(  # type: ignore[union-attr]
            cs,
            cls,
            vls,
        )
        return MetadataStructure(
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
        )

    @classmethod
    def from_model(self, msd: MetadataStructure) -> "JsonMetadataStructure":
        """Converts a pysdmx MSD to an SDMX-JSON one."""
        if not msd.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON metadata structures must have a name",
                {"metadata_structure": msd.id},
            )

        return JsonMetadataStructure(
            agency=(
                msd.agency.id if isinstance(msd.agency, Agency) else msd.agency
            ),
            id=msd.id,
            name=msd.name,
            version=msd.version,
            isExternalReference=msd.is_external_reference,
            validFrom=msd.valid_from,
            validTo=msd.valid_to,
            description=msd.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in msd.annotations]
            ),
            metadataStructureComponents=JsonMetadataComponents.from_model(
                msd.components
            ),
        )


class JsonMetadataStructures(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for metadata structures."""

    metadataStructures: Sequence[JsonMetadataStructure]
    conceptSchemes: Sequence[JsonConceptScheme] = ()
    valuelists: Sequence[JsonValuelist] = ()
    codelists: Sequence[JsonCodelist] = ()

    def to_model(self) -> Sequence[MetadataStructure]:
        """Returns the requested msds."""
        return [
            msd.to_model(
                self.conceptSchemes,
                self.codelists,
                self.valuelists,
            )
            for msd in self.metadataStructures
        ]


class JsonMetadataStructuresMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /metadatastructure queries."""

    data: JsonMetadataStructures

    def to_model(self) -> Sequence[MetadataStructure]:
        """Returns the requested metadata structures."""
        return self.data.to_model()
