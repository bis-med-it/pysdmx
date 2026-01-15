"""Collection of SDMX-JSON schemas for generic structure messages."""

from typing import Literal, Sequence

from msgspec import Struct

from pysdmx import errors
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
from pysdmx.io.json.sdmxjson2.messages.core import JsonHeader
from pysdmx.io.json.sdmxjson2.messages.dataflow import JsonDataflow
from pysdmx.io.json.sdmxjson2.messages.dsd import JsonDataStructure
from pysdmx.io.json.sdmxjson2.messages.map import (
    JsonRepresentationMap,
    JsonStructureMap,
)
from pysdmx.io.json.sdmxjson2.messages.metadataflow import JsonMetadataflow
from pysdmx.io.json.sdmxjson2.messages.mpa import (
    JsonMetadataProvisionAgreement,
)
from pysdmx.io.json.sdmxjson2.messages.msd import JsonMetadataStructure
from pysdmx.io.json.sdmxjson2.messages.pa import JsonProvisionAgreement
from pysdmx.io.json.sdmxjson2.messages.provider import (
    JsonDataProviderScheme,
    JsonMetadataProviderScheme,
)
from pysdmx.io.json.sdmxjson2.messages.vtl import (
    JsonCustomTypeScheme,
    JsonNamePersonalisationScheme,
    JsonRulesetScheme,
    JsonTransformationScheme,
    JsonUserDefinedOperatorScheme,
    JsonVtlMappingScheme,
)
from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.message import StructureMessage


class JsonStructures(Struct, frozen=True, omit_defaults=True):
    """The allowed strutures."""

    agencySchemes: Sequence[JsonAgencyScheme] = ()
    categorisations: Sequence[JsonCategorisation] = ()
    categorySchemes: Sequence[JsonCategoryScheme] = ()
    codelists: Sequence[JsonCodelist] = ()
    conceptSchemes: Sequence[JsonConceptScheme] = ()
    customTypeSchemes: Sequence[JsonCustomTypeScheme] = ()
    dataConstraints: Sequence[JsonDataConstraint] = ()
    dataflows: Sequence[JsonDataflow] = ()
    dataProviderSchemes: Sequence[JsonDataProviderScheme] = ()
    dataStructures: Sequence[JsonDataStructure] = ()
    hierarchies: Sequence[JsonHierarchy] = ()
    hierarchyAssociations: Sequence[JsonHierarchyAssociation] = ()
    metadataflows: Sequence[JsonMetadataflow] = ()
    metadataProviderSchemes: Sequence[JsonMetadataProviderScheme] = ()
    metadataProvisionAgreements: Sequence[JsonMetadataProvisionAgreement] = ()
    metadataStructures: Sequence[JsonMetadataStructure] = ()
    namePersonalisationSchemes: Sequence[JsonNamePersonalisationScheme] = ()
    provisionAgreements: Sequence[JsonProvisionAgreement] = ()
    representationMaps: Sequence[JsonRepresentationMap] = ()
    rulesetSchemes: Sequence[JsonRulesetScheme] = ()
    structureMaps: Sequence[JsonStructureMap] = ()
    transformationSchemes: Sequence[JsonTransformationScheme] = ()
    userDefinedOperatorSchemes: Sequence[JsonUserDefinedOperatorScheme] = ()
    valueLists: Sequence[JsonValuelist] = ()
    vtlMappingSchemes: Sequence[JsonVtlMappingScheme] = ()

    def to_model(self) -> Sequence[MaintainableArtefact]:
        """Map to pysdmx artefacts."""
        structures = []  # type: ignore[var-annotated]
        structures.extend(
            i.to_model(self.dataflows) for i in self.agencySchemes
        )
        structures.extend(i.to_model() for i in self.categorisations)
        structures.extend(i.to_model() for i in self.categorySchemes)
        structures.extend(i.to_model() for i in self.codelists)
        structures.extend(
            i.to_model(self.codelists) for i in self.conceptSchemes
        )
        structures.extend(i.to_model() for i in self.customTypeSchemes)
        structures.extend(i.to_model() for i in self.dataConstraints)
        structures.extend(
            i.to_model(
                self.dataStructures,
                self.conceptSchemes,
                self.valueLists,
                self.codelists,
            )
            for i in self.dataflows
        )
        structures.extend(
            i.to_model(self.provisionAgreements)
            for i in self.dataProviderSchemes
        )
        structures.extend(
            i.to_model(
                self.conceptSchemes, self.codelists, self.valueLists, ()
            )
            for i in self.dataStructures
        )
        structures.extend(i.to_model(self.codelists) for i in self.hierarchies)
        structures.extend(
            i.to_model(self.hierarchies, self.codelists)
            for i in self.hierarchyAssociations
        )

        structures.extend(i.to_model() for i in self.metadataflows)
        structures.extend(
            i.to_model(self.metadataProvisionAgreements)
            for i in self.metadataProviderSchemes
        )
        structures.extend(
            i.to_model() for i in self.metadataProvisionAgreements
        )
        structures.extend(
            i.to_model(self.conceptSchemes, self.codelists, self.valueLists)
            for i in self.metadataStructures
        )
        structures.extend(
            i.to_model() for i in self.namePersonalisationSchemes
        )
        structures.extend(i.to_model() for i in self.provisionAgreements)
        structures.extend(
            i.to_model(bool(len(i.source) > 1 or len(i.target) > 1))
            for i in self.representationMaps
        )
        structures.extend(i.to_model() for i in self.rulesetSchemes)
        structures.extend(
            i.to_model(self.representationMaps) for i in self.structureMaps
        )
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
        structures.extend(i.to_model() for i in self.valueLists)
        structures.extend(i.to_model() for i in self.vtlMappingSchemes)
        return structures

    @classmethod
    def from_model(cls, msg: StructureMessage) -> "JsonStructures":
        """Create an SDMX-JSON structures from a list of artefacts."""
        if not msg.structures:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON structure messages must have structures.",
            )
        codelists = tuple(
            [JsonCodelist.from_model(c) for c in msg.get_codelists()]
        )
        valuelists = tuple(
            [JsonValuelist.from_model(c) for c in msg.get_value_lists()]
        )
        agencies = tuple(
            [JsonAgencyScheme.from_model(a) for a in msg.get_agency_schemes()]
        )
        dataflows = tuple(
            [JsonDataflow.from_model(d) for d in msg.get_dataflows()]
        )
        agreements = tuple(
            [
                JsonProvisionAgreement.from_model(p)
                for p in msg.get_provision_agreements()
            ]
        )
        categorisations = tuple(
            [
                JsonCategorisation.from_model(c)
                for c in msg.get_categorisations()
            ]
        )
        hier_associations = tuple(
            [
                JsonHierarchyAssociation.from_model(ha)
                for ha in msg.get_hierarchy_associations()
            ]
        )
        category_schemes = tuple(
            [
                JsonCategoryScheme.from_model(cs)
                for cs in msg.get_category_schemes()
            ]
        )
        concept_schemes = tuple(
            [
                JsonConceptScheme.from_model(cs)
                for cs in msg.get_concept_schemes()
            ]
        )
        data_structures = tuple(
            [
                JsonDataStructure.from_model(ds)
                for ds in msg.get_data_structure_definitions()
            ]
        )
        data_providers = tuple(
            [
                JsonDataProviderScheme.from_model(dps)
                for dps in msg.get_data_provider_schemes()
            ]
        )
        representations_maps = tuple(
            [
                JsonRepresentationMap.from_model(rm)
                for rm in msg.get_representation_maps()
            ]
        )
        structure_maps = tuple(
            [
                JsonStructureMap.from_model(sm)
                for sm in msg.get_structure_maps()
            ]
        )
        custom_types = tuple(
            [
                JsonCustomTypeScheme.from_model(ct)
                for ct in msg.get_custom_type_schemes()
            ]
        )
        name_personalisations = tuple(
            [
                JsonNamePersonalisationScheme.from_model(np)
                for np in msg.get_name_personalisation_schemes()
            ]
        )
        user_operators = tuple(
            [
                JsonUserDefinedOperatorScheme.from_model(uo)
                for uo in msg.get_user_defined_operator_schemes()
            ]
        )
        rulesets = tuple(
            [
                JsonRulesetScheme.from_model(rs)
                for rs in msg.get_ruleset_schemes()
            ]
        )
        vtl_mappings = tuple(
            [
                JsonVtlMappingScheme.from_model(vm)
                for vm in msg.get_vtl_mapping_schemes()
            ]
        )
        transformations = tuple(
            [
                JsonTransformationScheme.from_model(ts)
                for ts in msg.get_transformation_schemes()
            ]
        )
        hierarchies = tuple(
            [JsonHierarchy.from_model(h) for h in msg.get_hierarchies()]
        )
        constraints = tuple(
            [
                JsonDataConstraint.from_model(c)
                for c in msg.get_data_constraints()
            ]
        )
        mpas = tuple(
            [
                JsonMetadataProvisionAgreement.from_model(c)
                for c in msg.get_metadata_provision_agreements()
            ]
        )
        mprvs = tuple(
            [
                JsonMetadataProviderScheme.from_model(c)
                for c in msg.get_metadata_provider_schemes()
            ]
        )
        mdfs = tuple(
            [JsonMetadataflow.from_model(c) for c in msg.get_metadataflows()]
        )
        msds = tuple(
            [
                JsonMetadataStructure.from_model(c)
                for c in msg.get_metadata_structures()
            ]
        )
        return JsonStructures(
            agencySchemes=agencies,
            categorisations=categorisations,
            categorySchemes=category_schemes,
            codelists=codelists,
            conceptSchemes=concept_schemes,
            customTypeSchemes=custom_types,
            dataConstraints=constraints,
            dataflows=dataflows,
            dataProviderSchemes=data_providers,
            dataStructures=data_structures,
            hierarchies=hierarchies,
            hierarchyAssociations=hier_associations,
            metadataflows=mdfs,
            metadataProviderSchemes=mprvs,
            metadataProvisionAgreements=mpas,
            metadataStructures=msds,
            namePersonalisationSchemes=name_personalisations,
            provisionAgreements=agreements,
            representationMaps=representations_maps,
            rulesetSchemes=rulesets,
            structureMaps=structure_maps,
            transformationSchemes=transformations,
            userDefinedOperatorSchemes=user_operators,
            valueLists=valuelists,
            vtlMappingSchemes=vtl_mappings,
        )


class JsonStructureMessage(Struct, frozen=True, omit_defaults=True):
    """A generic SDMX-JSON 2.0 Structure message."""

    meta: JsonHeader
    data: JsonStructures

    def to_model(self) -> StructureMessage:
        """Map to pysdmx message class."""
        header = self.meta.to_model()
        structures = self.data.to_model()
        return StructureMessage(header, structures)

    @classmethod
    def from_model(
        cls,
        message: StructureMessage,
        msg_version: Literal["2.0.0", "2.1.0"] = "2.0.0",
    ) -> "JsonStructureMessage":
        """Creates an SDMX-JSON payload from a pysdmx StructureMessage."""
        if not message.header:
            raise errors.Invalid(
                "Invalid input", "SDMX-JSON messages must have a header."
            )
        header = JsonHeader.from_model(message.header, msg_version=msg_version)
        structs = JsonStructures.from_model(message)
        return JsonStructureMessage(header, structs)
