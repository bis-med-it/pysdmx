"""Collection of SDMX-JSON schemas for VTL artefacts."""

from typing import Literal, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import (
    ItemSchemeType,
    JsonAnnotation,
    NameableType,
)
from pysdmx.model.__base import DataflowRef
from pysdmx.model.vtl import (
    CustomType,
    CustomTypeScheme,
    FromVtlMapping,
    NamePersonalisation,
    NamePersonalisationScheme,
    Ruleset,
    RulesetScheme,
    ToVtlMapping,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
    VtlMapping,
    VtlMappingScheme,
)
from pysdmx.util import parse_urn


class JsonCustomType(NameableType, frozen=True):
    """SDMX-JSON payload for custom types."""

    vtlScalarType: str = ""
    dataType: str = ""
    vtlLiteralFormat: Optional[str] = None
    outputFormat: Optional[str] = None
    nullValue: Optional[str] = None

    def to_model(self) -> CustomType:
        """Converts deserialized class to pysdmx model class."""
        return CustomType(
            id=self.id,
            name=self.name,
            description=self.description,
            data_type=self.dataType,
            null_value=self.nullValue,
            output_format=self.outputFormat,
            vtl_literal_format=self.vtlLiteralFormat,
            vtl_scalar_type=self.vtlScalarType,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonCustomTypeScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for custom type schemes."""

    vtlVersion: str = ""
    customTypes: Sequence[JsonCustomType] = ()

    def to_model(self) -> CustomTypeScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.customTypes]
        return CustomTypeScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonNamePersonalisation(NameableType, frozen=True):
    """SDMX-JSON payload for name personalisations."""

    vtlDefaultName: str = ""
    personalisedName: str = ""
    vtlArtefact: str = ""

    def to_model(self) -> NamePersonalisation:
        """Converts deserialized class to pysdmx model class."""
        return NamePersonalisation(
            self.id,
            name=self.name,
            description=self.description,
            vtl_default_name=self.vtlDefaultName,
            personalised_name=self.personalisedName,
            vtl_artefact=self.vtlArtefact,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonNamePersonalisationScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for name personalisation schemes."""

    vtlVersion: str = ""
    namePersonalisations: Sequence[JsonNamePersonalisation] = ()

    def to_model(self) -> NamePersonalisationScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.namePersonalisations]
        return NamePersonalisationScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonUserDefinedOperator(NameableType, frozen=True):
    """SDMX-JSON payload for user defined operator."""

    operatorDefinition: str = ""

    def to_model(self) -> UserDefinedOperator:
        """Converts deserialized class to pysdmx model class."""
        return UserDefinedOperator(
            self.id,
            name=self.name,
            description=self.description,
            operator_definition=self.operatorDefinition,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonUserDefinedOperatorScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for user defined operator schemes."""

    vtlVersion: str = ""
    userDefinedOperators: Sequence[JsonUserDefinedOperator] = ()
    vtlMappingScheme: Optional[str] = None
    rulesetSchemes: Sequence[str] = ()

    def to_model(self) -> UserDefinedOperatorScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.userDefinedOperators]
        return UserDefinedOperatorScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            vtl_mapping_scheme=self.vtlMappingScheme,
            ruleset_schemes=self.rulesetSchemes,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonRuleset(Struct, frozen=True):
    """SDMX-JSON payload for rulesets."""

    id: str
    name: str
    rulesetDefinition: str
    rulesetType: Literal["datapoint", "hierarchical"]
    rulesetScope: Literal["variable", "valuedomain"]
    description: Optional[str] = None
    annotations: Sequence[JsonAnnotation] = ()

    def to_model(self) -> Ruleset:
        """Converts deserialized class to pysdmx model class."""
        return Ruleset(
            id=self.id,
            name=self.name,
            description=self.description,
            ruleset_definition=self.rulesetDefinition,
            ruleset_type=self.rulesetType,
            ruleset_scope=self.rulesetScope,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonRulesetScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for ruleset schemes."""

    vtlVersion: str = ""
    rulesets: Sequence[JsonRuleset] = ()
    vtlMappingScheme: Optional[str] = None

    def to_model(self) -> RulesetScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.rulesets]
        return RulesetScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            vtl_mapping_scheme=self.vtlMappingScheme,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonToVtlMapping(Struct, frozen=True):
    """SDMX-JSON payload for To VTL mappings."""

    toVtlSubSpace: Sequence[str]
    type: Optional[str] = None

    def to_model(self) -> ToVtlMapping:
        """Converts deserialized class to pysdmx model class."""
        return ToVtlMapping(self.toVtlSubSpace, self.type)


class JsonFromVtlMapping(Struct, frozen=True):
    """SDMX-JSON payload for from VTL mappings."""

    fromVtlSuperSpace: Sequence[str]
    type: Optional[str] = None

    def to_model(self) -> FromVtlMapping:
        """Converts deserialized class to pysdmx model class."""
        return FromVtlMapping(self.fromVtlSuperSpace, self.type)


class JsonVtlMapping(NameableType, frozen=True):
    """SDMX-JSON payload for VTL mappings."""

    alias: str = ""
    concept: Optional[str] = None
    codelist: Optional[str] = None
    dataflow: Optional[str] = None
    genericDataflow: Optional[str] = None
    toVtlMapping: Optional[JsonToVtlMapping] = None
    fromVtlMapping: Optional[JsonFromVtlMapping] = None

    def to_model(self) -> VtlMapping:
        """Converts deserialized class to pysdmx model class."""
        if self.codelist:
            return VtlCodelistMapping(
                self.id,
                name=self.name,
                description=self.description,
                codelist=self.codelist,
                codelist_alias=self.alias,
            )
        elif self.concept:
            return VtlConceptMapping(
                self.id,
                name=self.name,
                description=self.description,
                concept=self.concept,
                concept_alias=self.alias,
            )
        else:
            reference = (
                parse_urn(self.dataflow)
                if self.dataflow
                else parse_urn(self.genericDataflow)  # type: ignore[arg-type]
            )
            dataflow = DataflowRef(
                id=reference.id,
                agency=reference.agency,
                version=reference.version,
            )
            return VtlDataflowMapping(
                self.id,
                name=self.name,
                description=self.description,
                dataflow=dataflow,
                dataflow_alias=self.alias,
                from_vtl_mapping_method=(
                    self.fromVtlMapping.to_model()
                    if self.fromVtlMapping
                    else None
                ),
                to_vtl_mapping_method=(
                    self.toVtlMapping.to_model() if self.toVtlMapping else None
                ),
                annotations=[a.to_model() for a in self.annotations],
            )


class JsonVtlMappingScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for VTL mapping schemes."""

    vtlMappings: Sequence[JsonVtlMapping] = ()
    vtlMappingScheme: Optional[str] = None

    def to_model(self) -> VtlMappingScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.vtlMappings]
        return VtlMappingScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonTransformation(Struct, frozen=True):
    """SDMX-JSON payload for VTL transformations."""

    id: str
    name: str
    expression: str
    result: str
    isPersistent: bool
    description: Optional[str] = None
    annotations: Sequence[JsonAnnotation] = ()

    def to_model(self) -> Transformation:
        """Converts deserialized class to pysdmx model class."""
        return Transformation(
            self.id,
            name=self.name,
            description=self.description,
            expression=self.expression,
            is_persistent=self.isPersistent,
            result=self.result,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonTransformationScheme(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for VTL transformation schemes."""

    vtlVersion: str = ""
    transformations: Sequence[JsonTransformation] = ()
    vtlMappingScheme: Optional[str] = None
    namePersonalisationScheme: Optional[str] = None
    customTypeScheme: Optional[str] = None
    rulesetSchemes: Sequence[str] = ()
    userDefinedOperatorSchemes: Sequence[str] = ()

    def to_model(
        self,
        custom_type_schemes: Sequence[JsonCustomTypeScheme],
        vtl_mapping_schemes: Sequence[JsonVtlMappingScheme],
        name_personalisation_schemes: Sequence[JsonNamePersonalisationScheme],
        ruleset_schemes: Sequence[JsonRulesetScheme],
        user_defined_operator_schemes: Sequence[JsonUserDefinedOperatorScheme],
    ) -> TransformationScheme:
        """Converts deserialized class to pysdmx model class."""
        cts = [i.to_model() for i in custom_type_schemes]
        vms = [i.to_model() for i in vtl_mapping_schemes]
        nps = [i.to_model() for i in name_personalisation_schemes]
        rss = [i.to_model() for i in ruleset_schemes]
        dos = [i.to_model() for i in user_defined_operator_schemes]
        items = [i.to_model() for i in self.transformations]
        return TransformationScheme(
            self.id,
            name=self.name,
            description=self.description,
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            vtl_mapping_scheme=vms[0] if vms else None,
            custom_type_scheme=cts[0] if cts else None,
            name_personalisation_scheme=nps[0] if nps else None,
            ruleset_schemes=rss,
            user_defined_operator_schemes=dos,
            annotations=[a.to_model() for a in self.annotations],
        )


class JsonVtlTransformations(Struct, frozen=True):
    """SDMX-JSON payload for VTL transformation schemes."""

    transformationSchemes: Sequence[JsonTransformationScheme]
    customTypeSchemes: Sequence[JsonCustomTypeScheme] = ()
    vtlMappingSchemes: Sequence[JsonVtlMappingScheme] = ()
    namePersonalisationSchemes: Sequence[JsonNamePersonalisationScheme] = ()
    rulesetSchemes: Sequence[JsonRulesetScheme] = ()
    userDefinedOperatorSchemes: Sequence[JsonUserDefinedOperatorScheme] = ()

    def to_model(self) -> TransformationScheme:
        """Converts deserialized class to pysdmx model class."""
        return self.transformationSchemes[0].to_model(
            self.customTypeSchemes,
            self.vtlMappingSchemes,
            self.namePersonalisationSchemes,
            self.rulesetSchemes,
            self.userDefinedOperatorSchemes,
        )


class JsonVtlTransformationsMessage(Struct, frozen=True):
    """SDMX-JSON payload for /transformationscheme queries."""

    data: JsonVtlTransformations

    def to_model(self) -> TransformationScheme:
        """Returns the requested transformation scheme."""
        return self.data.to_model()
