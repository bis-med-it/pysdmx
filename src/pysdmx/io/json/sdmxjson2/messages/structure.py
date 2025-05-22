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
    JsonNamePersonalisationScheme,
    JsonRulesetScheme,
    JsonTransformationScheme,
    JsonUserDefinedOperatorScheme,
    JsonVtlMappingScheme,
)
from pysdmx.model import (
    AgencyScheme,
    Categorisation,
    CategoryScheme,
    Codelist,
    ConceptScheme,
    CustomTypeScheme,
    DataConsumerScheme,
    Dataflow,
    DataflowInfo,
    DataProviderScheme,
    DataStructureDefinition,
    Hierarchy,
    HierarchyAssociation,
    MultiRepresentationMap,
    NamePersonalisationScheme,
    Organisation,
    ProvisionAgreement,
    RepresentationMap,
    RulesetScheme,
    StructureMap,
    TransformationScheme,
    UserDefinedOperatorScheme,
    VtlMappingScheme,
)
from pysdmx.model.message import Header, Message


class JsonHeader(Struct, frozen=True):
    """The message header."""

    id: str
    prepared: datetime
    sender: Organisation
    test: bool = False
    contentLanguages: Sequence[str] = ()
    name: Optional[str] = None
    receivers: Optional[Organisation] = None

    def to_model(self) -> Header:
        """Map to pysdmx header class."""
        return Header(self.id, self.test, self.prepared, self.sender)


class JsonStructures(Struct, frozen=True):
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

    def to_model(self) -> Sequence[
        AgencyScheme,
        Categorisation,
        CategoryScheme,
        CustomTypeScheme,
        Codelist,
        ConceptScheme,
        DataConsumerScheme,
        Dataflow,
        DataflowInfo,
        DataProviderScheme,
        DataStructureDefinition,
        Hierarchy,
        HierarchyAssociation,
        MultiRepresentationMap,
        NamePersonalisationScheme,
        ProvisionAgreement,
        RepresentationMap,
        RulesetScheme,
        StructureMap,
        TransformationScheme,
        UserDefinedOperatorScheme,
        VtlMappingScheme,
    ]:
        """Map to pysdmx artefacts."""
        structures = []
        structures.extend(
            i.to_model(
                self.conceptSchemes, self.codelists, self.valueLists, ()
            )
            for i in self.dataStructures
        )
        structures.extend(i.to_model() for i in self.categorySchemes)
        structures.extend(
            i.to_model(self.codelists) for i in self.conceptSchemes
        )
        structures.extend(i.to_model() for i in self.codelists)
        structures.extend(i.to_model() for i in self.valueLists)
        structures.extend(i.to_model(self.codelists) for i in self.hierarchies)
        structures.extend(
            i.to_model(self.hierarchies, self.codelists)
            for i in self.hierarchyAssociations
        )
        structures.extend(
            i.to_model(self.dataflows) for i in self.agencySchemes
        )
        structures.extend(
            i.to_model(self.provisionAgreements)
            for i in self.dataProviderSchemes
        )
        structures.extend(
            i.to_model(
                self.dataStructures,
                self.conceptSchemes,
                self.valueLists,
                self.codelists,
            )
            for i in self.dataflows
        )
        structures.extend(i.to_model() for i in self.provisionAgreements)
        structures.extend(
            i.to_model(self.representationMaps) for i in self.structureMaps
        )
        for rm in self.representationMaps:
            multi = bool(len(rm.source) > 1 or len(rm.target) > 1)
            structures.append(rm.to_model(multi))
        structures.extend(i.to_model() for i in self.categorisations)
        structures.extend(i.to_model() for i in self.customTypeSchemes)
        structures.extend(i.to_model() for i in self.vtlMappingSchemes)
        structures.extend(
            i.to_model() for i in self.namePersonalisationSchemes
        )
        structures.extend(i.to_model() for i in self.rulesetSchemes)
        structures.extend(
            i.to_model(
                self.customTypeSchemes,
                self.vtlMappingSchemes,
                self.namePersonalisationSchemes,
                self.rulesetSchemes,
                self.userDefinedOperatorSchemes,
            )
            for i in self.transformationSchemes
        )
        structures.extend(
            i.to_model() for i in self.userDefinedOperatorSchemes
        )
        return structures


class JsonStructureMessage(Struct, frozen=True):
    """A generic SDMX-JSON 2.0 Structure message."""

    meta: JsonHeader
    data: JsonStructures

    def to_model(self) -> Message:
        """Map to pysdmx message class."""
        header = self.meta.to_model()
        structures = self.data.to_model()
        return Message(header, structures)
