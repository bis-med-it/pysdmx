"""Collection of SDMX-JSON schemas for SDMX-REST schema queries."""

from typing import Dict, Literal, Optional, Sequence, Tuple

import msgspec

from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist, JsonValuelist
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConceptScheme
from pysdmx.io.json.sdmxjson2.messages.constraint import (
    JsonDataConstraint,
    JsonKeySet,
)
from pysdmx.io.json.sdmxjson2.messages.core import JsonHeader
from pysdmx.io.json.sdmxjson2.messages.dsd import JsonDataStructure
from pysdmx.model import Components, HierarchyAssociation, Schema
from pysdmx.model.dataflow import Group
from pysdmx.util import parse_item_urn


class JsonSchemas(msgspec.Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload schema structures."""

    conceptSchemes: Sequence[JsonConceptScheme]
    dataStructures: Sequence[JsonDataStructure]
    valuelists: Sequence[JsonValuelist] = ()
    codelists: Sequence[JsonCodelist] = ()
    dataConstraints: Sequence[JsonDataConstraint] = ()

    def to_model(
        self,
    ) -> Tuple[Components, Optional[Sequence[Group]], Optional[Sequence[str]]]:
        """Returns the requested schema."""
        comps = self.dataStructures[0].dataStructureComponents
        comps, grps = comps.to_model(  # type: ignore[union-attr,assignment]
            self.conceptSchemes,
            self.codelists,
            self.valuelists,
            self.dataConstraints,
        )
        keys = self.__process_keys()
        return comps, grps, keys  # type: ignore[return-value]

    def __extract_keys_dict(
        self, keysets: Sequence[JsonKeySet]
    ) -> Sequence[Dict[str, str]]:
        keys = []
        for ks in keysets:
            for k in ks.keys:
                keys.append({kv.id: kv.value for kv in k.keyValues})
        return keys

    def __infer_keys(self, keys_dict: Dict[str, str]) -> str:
        dimensions = [
            d.id
            for d in self.dataStructures[
                0
            ].dataStructureComponents.dimensionList.dimensions
        ]
        dim_values = [
            (keys_dict[d] if d in keys_dict else "*") for d in dimensions
        ]
        return ".".join(dim_values)

    def __process_keys(self) -> Optional[Sequence[str]]:
        keys = []
        for c in self.dataConstraints:
            if c.dataKeySets:
                keys_dicts = self.__extract_keys_dict(c.dataKeySets)
                keys.extend([self.__infer_keys(d) for d in keys_dicts])
        return list(set(keys))


class JsonSchemaMessage(msgspec.Struct, frozen=True, omit_defaults=True):
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
        components, groups, keys = self.data.to_model()
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
            keys=keys,
        )
