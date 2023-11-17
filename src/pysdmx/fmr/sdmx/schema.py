"""Collection of SDMX-JSON schemas for SDMX-REST schema queries."""
from typing import Sequence

from msgspec import Struct

from pysdmx.fmr.sdmx.code import JsonCodelist, JsonValuelist
from pysdmx.fmr.sdmx.concept import JsonConceptScheme
from pysdmx.fmr.sdmx.constraint import JsonContentConstraint
from pysdmx.fmr.sdmx.core import JsonHeader
from pysdmx.fmr.sdmx.dsd import JsonDataStructure
from pysdmx.model import Components, Schema


class JsonSchemas(
    Struct,
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
    Struct,
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
    ) -> Schema:
        """Returns the requested schema."""
        components = self.data.to_model()
        urns = [a.urn for a in self.meta.links]
        return Schema(context, agency, id_, components, version, urns)
