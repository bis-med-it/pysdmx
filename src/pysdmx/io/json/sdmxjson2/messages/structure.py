"""Collection of SDMX-JSON schemas for generic structure messages."""

from datetime import datetime
from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.agency import JsonAgencyScheme
from pysdmx.io.json.sdmxjson2.messages.category import (
    JsonCategorisation,
    JsonCategoryScheme,
)
from pysdmx.io.json.sdmxjson2.messages.code import (
    JsonCodelist,
    JsonHierarchy,
    JsonHierarchyAssociation,
    JsonValuelist,
)
from pysdmx.io.json.sdmxjson2.messages.concept import JsonConceptScheme
from pysdmx.io.json.sdmxjson2.messages.constraint import JsonDataConstraint
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflow
from pysdmx.io.json.sdmxjson2.messages.dsd import JsonDataStructure
from pysdmx.io.json.sdmxjson2.messages.map import (
    JsonRepresentationMap,
    JsonStructureMap,
)
from pysdmx.io.json.sdmxjson2.messages.pa import JsonProvisionAgreement
from pysdmx.io.json.sdmxjson2.messages.provider import JsonDataProviderScheme
from pysdmx.io.json.sdmxjson2.messages.vtl import (
    JsonCustomTypeScheme,
    JsonVtlMappingScheme,
    JsonNamePersonalisationScheme,
    JsonRulesetScheme,
    JsonTransformationScheme,
    JsonUserDefinedOperatorScheme,
)
from pysdmx.model import Organisation


class Header(Struct, frozen=True):
    """The message header."""

    id: str
    prepared: datetime
    sender: Organisation
    test: bool = False
    contentLanguages: Sequence[str] = ()
    name: Optional[str] = None
    receivers: Optional[Organisation] = None


class Structures(Struct, frozen=True):
    """The allowed strutures."""

    dataStructures: Sequence[JsonDataStructure] = ()
    categorySchemes: Sequence[JsonCategoryScheme] = ()
    conceptSchemes: Sequence[JsonConceptScheme] = ()
    codelists: Sequence[JsonCodelist] = ()
    valueLists: Sequence[JsonValuelist] = ()
    hierarchies: Sequence[JsonHierarchy] = ()
    hierarchyAssociations: Sequence[JsonHierarchyAssociation] = ()
    agencySchemes: Sequence[JsonAgencyScheme] = ()
    dataProviderSchemes: Sequence[JsonDataProviderScheme] = ()
    dataflows: Sequence[JsonDataflow] = ()
    provisionAgreements: Sequence[JsonProvisionAgreement] = ()
    structureMaps: Sequence[JsonStructureMap] = ()
    representationMaps: Sequence[JsonRepresentationMap] = ()
    categorisations: Sequence[JsonCategorisation] = ()
    customTypeSchemes: Sequence[JsonCustomTypeScheme] = ()
    vtlMappingSchemes: Sequence[JsonVtlMappingScheme] = ()
    namePersonalisationSchemes: Sequence[JsonNamePersonalisationScheme] = ()
    rulesetSchemes: Sequence[JsonRulesetScheme] = ()
    transformationSchemes: Sequence[JsonTransformationScheme] = ()
    userDefinedOperatorSchemes: Sequence[JsonUserDefinedOperatorScheme] = ()


class StructureMessage(Struct, frozen=True):
    """A generic SDMX-JSON 2.0 Structure message."""

    meta: Header
    data: Structures
