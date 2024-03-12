"""Collection of SDMX-JSON schemas for SDMX-REST schema queries."""

from typing import Sequence

import msgspec

from pysdmx.fmr.sdmx.code import JsonCodelist, JsonValuelist
from pysdmx.fmr.sdmx.concept import JsonConceptScheme
from pysdmx.fmr.sdmx.constraint import JsonContentConstraint
from pysdmx.fmr.sdmx.core import JsonHeader
from pysdmx.fmr.sdmx.dsd import JsonDataStructure
from pysdmx.model import Components, HierarchyAssociation, Schema
from pysdmx.util import parse_item_urn


class JsonSchemas(
    msgspec.Struct,
    frozen=True,
):
    """SDMX-JSON payload schema structures."""

    conceptSchemes: Sequence[JsonConceptScheme]
    dataStructures: Sequence[JsonDataStructure]
    valuelists: Sequence[JsonValuelist] = ()
    codelists: Sequence[JsonCodelist] = ()
    contentConstraints: Sequence[JsonContentConstraint] = ()

    def to_model(self) -> Components:
        """Returns the requested schema."""
        cls = [cl.to_model() for cl in self.codelists]
        cls.extend([vl.to_model() for vl in self.valuelists])
        return self.dataStructures[0].dataStructureComponents.to_model(
            self.conceptSchemes, cls, self.contentConstraints
        )


class JsonSchemaMessage(
    msgspec.Struct,
    frozen=True,
):
    """SDMX-JSON payload for /schema queries."""

    meta: JsonHeader
    data: JsonSchemas

    def to_model(
        self,
        context: str,
        agency: str,
        id_: str,
        version: str,
        hierarchies: Sequence[HierarchyAssociation],
    ) -> Schema:
        """Returns the requested schema."""
        components = self.data.to_model()
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
