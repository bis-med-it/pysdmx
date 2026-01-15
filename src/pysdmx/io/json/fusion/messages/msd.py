"""Collection of Fusion-JSON schemas for SDMX-REST schema queries."""

from typing import Literal, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.io.json.fusion.messages.code import FusionCodelist
from pysdmx.io.json.fusion.messages.concept import FusionConceptScheme
from pysdmx.io.json.fusion.messages.core import (
    FusionRepresentation,
    FusionString,
)
from pysdmx.io.json.fusion.messages.dsd import (
    _find_concept,
    _get_representation,
)
from pysdmx.model import ArrayBoundaries, MetadataComponent
from pysdmx.model import MetadataStructure as MSD
from pysdmx.util import parse_item_urn


class FusionMetadataAttribute(Struct, frozen=True):
    """Fusion-JSON payload for a metadata attribute."""

    id: str
    concept: str
    minOccurs: int
    maxOccurs: Union[int, Literal["unbounded"]] = "unbounded"
    presentational: Optional[bool] = False
    representation: Optional[FusionRepresentation] = None
    metadataAttributes: Sequence["FusionMetadataAttribute"] = ()

    def to_model(
        self,
        cs: Sequence[FusionConceptScheme],
        cls: Sequence[FusionCodelist],
    ) -> MetadataComponent:
        """Returns an attribute."""
        m = _find_concept(cs, self.concept) if cs else None
        c = m.to_model(cls) if m else parse_item_urn(self.concept)
        dt, facets, codes, _ = _get_representation(
            self.id, self.representation, cls, {}
        )

        if self.representation and self.representation.representation:
            local_enum_ref = self.representation.representation
        else:
            local_enum_ref = None

        if self.maxOccurs == "unbounded":
            ab = ArrayBoundaries(self.minOccurs)
        elif self.maxOccurs > 1:
            ab = ArrayBoundaries(self.minOccurs, self.maxOccurs)
        else:
            ab = None

        return MetadataComponent(
            self.id,
            is_presentational=self.presentational,  # type: ignore[arg-type]
            concept=c,
            local_dtype=dt,
            local_facets=facets,
            local_codes=codes,
            array_def=ab,
            local_enum_ref=local_enum_ref,
            components=[
                ma.to_model(cs, cls) for ma in self.metadataAttributes
            ],
        )


class FusionMetadataStructure(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for an MSD."""

    id: str
    names: Sequence[FusionString]
    agency: str
    descriptions: Optional[Sequence[FusionString]] = None
    version: str = "1.0"
    metadataAttributes: Sequence[FusionMetadataAttribute] = ()

    def to_model(
        self,
        cs: Sequence[FusionConceptScheme],
        cls: Sequence[FusionCodelist],
    ) -> MSD:
        """Returns the schema for this DSD."""
        return MSD(
            id=self.id,
            agency=self.agency,
            name=self.names[0].value if self.names else None,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            components=[a.to_model(cs, cls) for a in self.metadataAttributes],
        )


class FusionMetadataStructuresMessage(Struct, frozen=True):
    """Fusion-JSON payload for /metadatastructure queries."""

    ConceptScheme: Sequence[FusionConceptScheme]
    MetadataStructure: Sequence[FusionMetadataStructure]
    ValueList: Sequence[FusionCodelist] = ()
    Codelist: Sequence[FusionCodelist] = ()

    def to_model(self) -> Sequence[MSD]:
        """Returns the requested metadata structures."""
        all_mds = []
        for msd in self.MetadataStructure:
            cls: list[FusionCodelist] = []
            cls.extend(self.Codelist)
            cls.extend(self.ValueList)
            all_mds.append(msd.to_model(self.ConceptScheme, cls))
        return all_mds
