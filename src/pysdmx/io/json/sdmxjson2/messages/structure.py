"""Collection of SDMX-JSON schemas for generic structure messages."""

from datetime import datetime
from typing import Dict, Optional, Sequence

from msgspec import Struct

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
from pysdmx.io.json.sdmxjson2.messages.org import (
    JsonAgencyScheme,
    JsonDataProviderScheme,
)
from pysdmx.io.json.sdmxjson2.messages.pa import JsonProvisionAgreement
from pysdmx.model import Organisation


class Header(Struct, frozen=True):
    """The message header."""

    id: str
    prepared: datetime
    sender: Organisation
    test: bool = False
    content_languages: Sequence[str] = ()
    name: Optional[str] = None
    names: Optional[Dict[str, str]] = None
    receivers: Optional[Organisation] = None


class Structures(Struct, frozen=True):
    """The allowed strutures."""

    data_structures: Sequence[JsonDataStructure] = ()
    category_schemes: Sequence[JsonCategoryScheme] = ()
    concept_schemes: Sequence[JsonConceptScheme] = ()
    codelists: Sequence[JsonCodelist] = ()
    value_lists: Sequence[JsonValuelist] = ()
    hierarchies: Sequence[JsonHierarchy] = ()
    hierarchy_associations: Sequence[JsonHierarchyAssociation] = ()
    agency_schemes: Sequence[JsonAgencyScheme] = ()
    data_provider_schemes: Sequence[JsonDataProviderScheme] = ()
    dataflows: Sequence[JsonDataflow] = ()
    provision_agreements: Sequence[JsonProvisionAgreement] = ()
    structure_maps: Sequence[JsonStructureMap] = ()
    representation_maps: Sequence[JsonRepresentationMap] = ()
    categorisations: Sequence[JsonCategorisation] = ()
    dataConstraints: Sequence[JsonDataConstraint] = ()


class StructureMessage(Struct, frozen=True):
    """A generic SDMX-JSON 2.0 Structure message."""

    meta: Header
    data: Structures
