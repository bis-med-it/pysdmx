"""Collection of Fusion-JSON schemas for concepts."""

from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.code import FusionCodelist
from pysdmx.io.json.fusion.messages.core import (
    FusionRepresentation,
    FusionString,
)
from pysdmx.model.concept import Concept, ConceptScheme as CS, DataType


class FusionConcept(Struct, frozen=True):
    """Fusion-JSON payload for concepts."""

    id: str
    names: Sequence[FusionString]
    representation: Optional[FusionRepresentation] = None
    descriptions: Optional[Sequence[FusionString]] = None

    def to_model(self, codelists: Sequence[FusionCodelist]) -> Concept:
        """Converts a FusionConcept to a standard concept."""
        dt = (
            DataType(self.representation.textFormat.textType)
            if self.representation and self.representation.textFormat
            else DataType.STRING
        )
        f = self.representation.to_facets() if self.representation else None
        c = (
            self.representation.to_enumeration(codelists, [])
            if self.representation
            else None
        )
        d = self.descriptions[0].value if self.descriptions else None
        cl_ref = (
            self.representation.representation
            if self.representation and c
            else None
        )
        return Concept(
            id=self.id,
            dtype=dt,
            facets=f,
            name=self.names[0].value,
            description=d,
            codes=c,
            enum_ref=cl_ref,
        )


class FusionConceptScheme(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a concept scheme."""

    id: str
    names: Sequence[FusionString]
    agency: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"
    items: Sequence[FusionConcept] = ()

    def to_model(self, codelists: Sequence[FusionCodelist]) -> CS:
        """Converts a FusionConceptScheme to a standard concept scheme."""
        d = self.descriptions[0].value if self.descriptions else None
        return CS(
            id=self.id,
            name=self.names[0].value,
            agency=self.agency,
            description=d,
            version=self.version,
            items=[c.to_model(codelists) for c in self.items],
        )


class FusionConceptSchemeMessage(
    Struct,
    frozen=True,
):
    """Fusion-JSON payload for /conceptscheme queries."""

    Codelist: Sequence[FusionCodelist]
    ConceptScheme: Sequence[FusionConceptScheme]

    def to_model(self) -> CS:
        """Returns the requested concept scheme."""
        return self.ConceptScheme[0].to_model(self.Codelist)
