"""Collection of SDMX-JSON schemas for SDMX-REST schema queries."""

from typing import Literal, Optional, Sequence, Tuple

import msgspec

from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist, JsonValuelist
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConceptScheme
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.io.json.sdmxjson2.messages.core import JsonHeader
from pysdmx.io.json.sdmxjson2.messages.dsd import JsonDataStructure
from pysdmx.model import Components, HierarchyAssociation, Schema
from pysdmx.model.dataflow import GroupDimension
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
    contentConstraints: Sequence[JsonDataConstraint] = ()

    def to_model(
        self,
    ) -> Tuple[Components, Optional[Sequence[GroupDimension]]]:
        """Returns the requested schema."""
        comps = self.dataStructures[0].dataStructureComponents
        grps = self.dataStructures[0].dataStructureComponents.groups
        comps = comps.to_model(  # type: ignore[union-attr]
            self.conceptSchemes,
            self.codelists,
            self.valuelists,
            self.contentConstraints,
        )
        grps = [
            GroupDimension(g.id, dimensions=g.groupDimensions) for g in grps
        ]
        return comps, grps


class JsonSchemaMessage(
    msgspec.Struct,
    frozen=True,
):
    """SDMX-JSON payload for /schema queries."""

    meta: JsonHeader
    data: JsonSchemas

    def to_model(
        self,
        context: Literal["datastructure", "dataflow", "provisionagreement"],
        agency: str,
        id_: str,
        version: str,
        hierarchies: Sequence[HierarchyAssociation],
    ) -> Schema:
        """Returns the requested schema."""
        components, groups = self.data.to_model()
        comp_dict = {c.id: c for c in components}
        urns = [a.urn for a in self.meta.links]
        for ha in hierarchies:
            comp_id = parse_item_urn(ha.component_ref).item_id
            h = msgspec.structs.replace(  # type: ignore[type-var]
                ha.hierarchy,
                operator=ha.operator,
            )
            comp_dict[comp_id] = msgspec.structs.replace(
                components[comp_id], local_codes=h
            )
            urns.append(
                "urn:sdmx:org.sdmx.infomodel.codelist.Hierarchy="
                f"{h.agency}:{h.id}({h.version})"  # type: ignore[union-attr]
            )
        comps = Components(comp_dict.values())
        return Schema(
            context,
            agency,
            id_,
            comps,
            version,
            urns,  # type: ignore[arg-type]
            groups=groups,
        )
