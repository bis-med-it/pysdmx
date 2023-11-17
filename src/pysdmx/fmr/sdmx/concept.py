"""Collection of SDMX-JSON schemas for concepts."""

from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.fmr.sdmx.code import JsonCodelist
from pysdmx.fmr.sdmx.core import JsonRepresentation
from pysdmx.model import Concept, ConceptScheme, DataType


class JsonConcept(Struct, frozen=True):
    """SDMX-JSON payload for concepts."""

    id: str
    coreRepresentation: Optional[JsonRepresentation] = None
    name: Optional[str] = None
    description: Optional[str] = None

    def to_model(self, codelists: Sequence[JsonCodelist]) -> Concept:
        """Converts a JsonConcept to a standard concept."""
        repr_ = self.coreRepresentation
        if repr_:
            if repr_.enumerationFormat:
                dt = DataType(
                    repr_.enumerationFormat.textType,
                )
            else:
                dt = DataType(
                    repr_.format.textType,  # type: ignore[union-attr]
                )
            facets = repr_.to_facets()
            codes = repr_.to_enumeration(
                [cl.to_model() for cl in codelists], []
            )
            cl_ref = repr_.enumeration
        else:
            dt = DataType.STRING
            facets = None
            codes = []
            cl_ref = None
        return Concept(
            self.id,
            dtype=dt,
            facets=facets,
            name=self.name,
            description=self.description,
            codes=codes,
            enum_ref=cl_ref,
        )


class JsonConceptScheme(Struct, frozen=True, rename={"agency": "agencyID"}):
    """SDMX-JSON payload for a concept scheme."""

    id: str
    name: str
    agency: str
    description: Optional[str] = None
    version: str = "1.0"
    concepts: Sequence[JsonConcept] = ()

    def to_model(self, codelists: Sequence[JsonCodelist]) -> ConceptScheme:
        """Converts a JsonConceptScheme to a standard concept scheme."""
        return ConceptScheme(
            self.id,
            self.name,
            self.agency,
            self.description,
            self.version,
            [c.to_model(codelists) for c in self.concepts],
        )


class JsonConceptSchemes(
    Struct,
    frozen=True,
):
    """SDMX-JSON payload for the list of concept schemes."""

    codelists: Sequence[JsonCodelist]
    conceptSchemes: Sequence[JsonConceptScheme]


class JsonConcepSchemeMessage(
    Struct,
    frozen=True,
):
    """SDMX-JSON payload for /conceptscheme queries."""

    data: JsonConceptSchemes

    def to_model(self) -> ConceptScheme:
        """Returns the requested concept scheme."""
        return self.data.conceptSchemes[0].to_model(self.data.codelists)
