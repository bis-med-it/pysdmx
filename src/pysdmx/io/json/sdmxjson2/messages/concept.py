"""Collection of SDMX-JSON schemas for concepts."""

from typing import Optional, Sequence

import msgspec

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist
from pysdmx.io.json.sdmxjson2.messages.core import (
    ItemSchemeType,
    JsonAnnotation,
    JsonRepresentation,
    NameableType,
)
from pysdmx.model import Agency, Codelist, Concept, ConceptScheme, DataType


class IsoConceptReference(msgspec.Struct, frozen=True, omit_defaults=True):
    """Payload for a reference to an ISO 11179 concept."""

    conceptAgency: str
    conceptSchemeID: str
    conceptID: str


class JsonConcept(NameableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for concepts."""

    coreRepresentation: Optional[JsonRepresentation] = None
    parent: Optional[str] = None
    isoConceptReference: Optional[IsoConceptReference] = None

    def to_model(self, codelists: Sequence[Codelist]) -> Concept:
        """Converts a JsonConcept to a standard concept."""
        repr_ = self.coreRepresentation
        if repr_:
            if repr_.enumerationFormat:
                dt = DataType(repr_.enumerationFormat.dataType)
            elif repr_.format:
                dt = DataType(repr_.format.dataType)
            else:
                dt = DataType.STRING
            facets = repr_.to_facets()
            codes = repr_.to_enumeration(codelists, [])
            cl_ref = repr_.enumeration
        else:
            dt = DataType.STRING
            facets = None
            codes = None
            cl_ref = None
        return Concept(
            id=self.id,
            dtype=dt,
            facets=facets,
            name=self.name,
            description=self.description,
            codes=codes,
            enum_ref=cl_ref,
        )

    @classmethod
    def from_model(self, concept: Concept) -> "JsonConcept":
        """Converts a pysdmx concept to an SDMX-JSON one."""
        if not concept.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON concepts must have a name",
                {"codelist": concept.id},
            )
        if concept.codes:
            enum_ref = (
                "urn:sdmx:org.sdmx.infomodel.codelist."
                f"{concept.codes.short_urn}"
            )
        elif concept.enum_ref:
            enum_ref = concept.enum_ref
        else:
            enum_ref = None

        return JsonConcept(
            id=concept.id,
            name=concept.name,
            description=concept.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in concept.annotations]
            ),
            coreRepresentation=JsonRepresentation.from_model(
                concept.dtype, enum_ref, concept.facets, None
            ),
        )


class JsonConceptScheme(ItemSchemeType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a concept scheme."""

    concepts: Sequence[JsonConcept] = ()

    def __set_urn(self, concept: Concept) -> Concept:
        urn = (
            "urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept="
            f"{self.agency}:{self.id}({self.version}).{concept.id}"
        )
        return msgspec.structs.replace(concept, urn=urn)

    def to_model(self, codelists: Sequence[JsonCodelist]) -> ConceptScheme:
        """Converts a JsonConceptScheme to a standard concept scheme."""
        cls = [cl.to_model() for cl in codelists]
        concepts = [c.to_model(cls) for c in self.concepts]
        concepts = [self.__set_urn(c) for c in concepts]
        return ConceptScheme(
            id=self.id,
            name=self.name,
            agency=self.agency,
            description=self.description,
            version=self.version,
            items=concepts,
            annotations=[a.to_model() for a in self.annotations],
            is_external_reference=self.isExternalReference,
            is_partial=self.isPartial,
            valid_from=self.validFrom,
            valid_to=self.validTo,
        )

    @classmethod
    def from_model(self, cs: ConceptScheme) -> "JsonConceptScheme":
        """Converts a pysdmx concept scheme to an SDMX-JSON one."""
        if not cs.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON concept schemes must have a name",
                {"concept_scheme": cs.id},
            )
        return JsonConceptScheme(
            agency=(
                cs.agency.id if isinstance(cs.agency, Agency) else cs.agency
            ),
            id=cs.id,
            name=cs.name,
            version=cs.version,
            isExternalReference=cs.is_external_reference,
            validFrom=cs.valid_from,
            validTo=cs.valid_to,
            description=cs.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in cs.annotations]
            ),
            isPartial=cs.is_partial,
            concepts=tuple([JsonConcept.from_model(c) for c in cs.concepts]),
        )


class JsonConceptSchemes(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of concept schemes."""

    conceptSchemes: Sequence[JsonConceptScheme]
    codelists: Sequence[JsonCodelist] = ()


class JsonConceptSchemeMessage(
    msgspec.Struct, frozen=True, omit_defaults=True
):
    """SDMX-JSON payload for /conceptscheme queries."""

    data: JsonConceptSchemes

    def to_model(self) -> ConceptScheme:
        """Returns the requested concept scheme."""
        return self.data.conceptSchemes[0].to_model(self.data.codelists)
