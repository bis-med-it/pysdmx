"""Collection of Fusion-JSON schemas for SDMX-REST schema queries."""
from typing import List, Sequence

from msgspec import Struct

from pysdmx.fmr.fusion.code import FusionCodelist
from pysdmx.fmr.fusion.concept import FusionConceptScheme
from pysdmx.fmr.fusion.constraint import FusionContentConstraint
from pysdmx.fmr.fusion.dsd import FusionDataStructure
from pysdmx.model import Schema


class FusionLink(Struct, frozen=True):
    """Fusion-JSON payload for link objects."""

    urn: str


class FusionHeader(Struct, frozen=True):
    """Fusion-JSON payload for message header."""

    links: Sequence[FusionLink] = ()


class FusionSchemaMessage(
    Struct,
    frozen=True,
):
    """Fusion-JSON payload for /schema queries."""

    meta: FusionHeader
    ConceptScheme: Sequence[FusionConceptScheme]
    DataStructure: Sequence[FusionDataStructure]
    ValueList: Sequence[FusionCodelist] = ()
    Codelist: Sequence[FusionCodelist] = ()
    DataConstraint: Sequence[FusionContentConstraint] = ()

    def to_model(
        self,
        context: str,
        agency: str,
        id_: str,
        version: str,
    ) -> Schema:
        """Returns the requested schema."""
        cls: List[FusionCodelist] = []
        cls.extend(self.Codelist)
        cls.extend(self.ValueList)
        components = self.DataStructure[0].get_components(
            self.ConceptScheme, cls, self.DataConstraint
        )
        urns = [a.urn for a in self.meta.links]
        return Schema(context, agency, id_, components, version, urns)
