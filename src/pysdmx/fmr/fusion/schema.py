"""Collection of Fusion-JSON schemas for SDMX-REST schema queries."""

from typing import List, Sequence

import msgspec

from pysdmx.fmr.fusion.code import FusionCodelist
from pysdmx.fmr.fusion.concept import FusionConceptScheme
from pysdmx.fmr.fusion.constraint import FusionContentConstraint
from pysdmx.fmr.fusion.core import FusionLink
from pysdmx.fmr.fusion.dsd import FusionDataStructure
from pysdmx.model import Components, HierarchyAssociation, Schema
from pysdmx.util import parse_item_urn


class FusionHeader(msgspec.Struct, frozen=True):
    """Fusion-JSON payload for message header."""

    links: Sequence[FusionLink] = ()


class FusionSchemaMessage(msgspec.Struct, frozen=True):
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
        hierarchies: Sequence[HierarchyAssociation],
    ) -> Schema:
        """Returns the requested schema."""
        cls: List[FusionCodelist] = []
        cls.extend(self.Codelist)
        cls.extend(self.ValueList)
        components = self.DataStructure[0].get_components(
            self.ConceptScheme, cls, self.DataConstraint
        )
        comp_dict = {c.id: c for c in components}
        urns = [a.urn for a in self.meta.links]
        for ha in hierarchies:
            comp_id = parse_item_urn(ha.component_ref).item_id
            h = msgspec.structs.replace(ha.hierarchy, operator=ha.operator)
            comp_dict[comp_id] = msgspec.structs.replace(
                components[comp_id], codes=h
            )
            urns.append(
                "urn:sdmx:org.sdmx.infomodel.codelist.Hierarchy="
                f"{h.agency}:{h.id}({h.version})"
            )
        comps = Components(comp_dict.values())
        return Schema(context, agency, id_, comps, version, urns)
