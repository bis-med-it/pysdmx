"""Collection of Fusion-JSON schemas for VTL artefacts."""

from datetime import datetime
from typing import Literal, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
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
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
    VtlMapping,
    VtlMappingScheme,
)
from pysdmx.model.vtl import (
    TransformationScheme as TS,
)
from pysdmx.util import parse_urn


class FusionCustomType(Struct, frozen=True):
    """Fusion-JSON payload for custom types."""

    id: str
    vtlScalarType: str
    dataType: str
    names: Sequence[FusionString] = ()
    vtlLiteralFormat: Optional[str] = None
    outputFormat: Optional[str] = None
    nullValue: Optional[str] = None
    descriptions: Sequence[FusionString] = ()

    def to_model(self) -> CustomType:
        """Converts deserialized class to pysdmx model class."""
        return CustomType(
            id=self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            data_type=self.dataType,
            null_value=self.nullValue,
            output_format=self.outputFormat,
            vtl_literal_format=self.vtlLiteralFormat,
            vtl_scalar_type=self.vtlScalarType,
        )


class FusionCustomTypeScheme(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for custom type schemes."""

    id: str
    agency: str
    vtlVersion: str
    names: Sequence[FusionString] = ()
    items: Sequence[FusionCustomType] = ()
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    isPartial: bool = False

    def to_model(self) -> CustomTypeScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.items]
        return CustomTypeScheme(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
        )


class FusionNamePersonalisation(Struct, frozen=True):
    """Fusion-JSON payload for name personalisations."""

    id: str
    vtlDefaultName: str
    personalisedName: str
    vtlArtefact: str
    names: Sequence[FusionString] = ()
    descriptions: Sequence[FusionString] = ()

    def to_model(self) -> NamePersonalisation:
        """Converts deserialized class to pysdmx model class."""
        return NamePersonalisation(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            vtl_default_name=self.vtlDefaultName,
            personalised_name=self.personalisedName,
            vtl_artefact=self.vtlArtefact,
        )


class FusionNamePersonalisationScheme(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for name personalisation schemes."""

    id: str
    agency: str
    vtlVersion: str
    names: Sequence[FusionString] = ()
    items: Sequence[FusionNamePersonalisation] = ()
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    isPartial: bool = False

    def to_model(self) -> NamePersonalisationScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.items]
        return NamePersonalisationScheme(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
        )


class FusionUserDefinedOperator(Struct, frozen=True):
    """Fusion-JSON payload for user defined operator."""

    id: str
    operatorDefinition: str
    names: Sequence[FusionString] = ()
    descriptions: Sequence[FusionString] = ()

    def to_model(self) -> UserDefinedOperator:
        """Converts deserialized class to pysdmx model class."""
        return UserDefinedOperator(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            operator_definition=self.operatorDefinition,
        )


class FusionUserDefinedOperatorScheme(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for user defined operator schemes."""

    id: str
    agency: str
    vtlVersion: str
    names: Sequence[FusionString] = ()
    items: Sequence[FusionUserDefinedOperator] = ()
    vtlMappingScheme: Optional[str] = None
    rulesetSchemes: Sequence[str] = ()
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    isPartial: bool = False

    def to_model(self) -> UserDefinedOperatorScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.items]
        return UserDefinedOperatorScheme(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
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
        )


class FusionRuleset(Struct, frozen=True):
    """Fusion-JSON payload for rulesets."""

    id: str
    rulesetDefinition: str
    rulesetType: Literal["datapoint", "hierarchical"]
    rulesetScope: Literal["variable", "valuedomain"]
    names: Sequence[FusionString] = ()
    descriptions: Sequence[FusionString] = ()

    def to_model(self) -> Ruleset:
        """Converts deserialized class to pysdmx model class."""
        return Ruleset(
            id=self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            ruleset_definition=self.rulesetDefinition,
            ruleset_type=self.rulesetType,
            ruleset_scope=self.rulesetScope,
        )


class FusionRulesetScheme(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for ruleset schemes."""

    id: str
    agency: str
    vtlVersion: str
    names: Sequence[FusionString] = ()
    items: Sequence[FusionRuleset] = ()
    vtlMappingScheme: Optional[str] = None
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    isPartial: bool = False

    def to_model(self) -> RulesetScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.items]
        return RulesetScheme(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
            vtl_version=self.vtlVersion,
            vtl_mapping_scheme=self.vtlMappingScheme,
        )


class FusionVtlMapping(Struct, frozen=True):
    """Fusion-JSON payload for VTL mappings."""

    id: str
    alias: str
    mapped: str
    names: Sequence[FusionString] = ()
    descriptions: Sequence[FusionString] = ()
    toVtlMethod: Optional[str] = None
    toVtlSubSpace: Sequence[str] = ()
    fromVtlMethod: Optional[str] = None
    fromVtlSuperSpace: Sequence[str] = ()

    def to_model(self) -> VtlMapping:
        """Converts deserialized class to pysdmx model class."""
        if "Codelist=" in self.mapped:
            return VtlCodelistMapping(
                self.id,
                name=self.names[0].value,
                description=(
                    self.descriptions[0].value if self.descriptions else None
                ),
                codelist=self.mapped,
                codelist_alias=self.alias,
            )
        elif "Concept" in self.mapped:
            return VtlConceptMapping(
                self.id,
                name=self.names[0].value,
                description=(
                    self.descriptions[0].value if self.descriptions else None
                ),
                concept=self.mapped,
                concept_alias=self.alias,
            )
        else:
            reference = parse_urn(self.mapped)
            dataflow = DataflowRef(
                id=reference.id,
                agency=reference.agency,
                version=reference.version,
            )
            return VtlDataflowMapping(
                self.id,
                name=self.names[0].value,
                description=(
                    self.descriptions[0].value if self.descriptions else None
                ),
                dataflow=dataflow,
                dataflow_alias=self.alias,
                from_vtl_mapping_method=(
                    FromVtlMapping(self.fromVtlSuperSpace, self.fromVtlMethod)
                    if self.fromVtlMethod
                    else None
                ),
                to_vtl_mapping_method=(
                    ToVtlMapping(self.toVtlSubSpace, self.toVtlMethod)
                    if self.toVtlMethod
                    else None
                ),
            )


class FusionVtlMappingScheme(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for VTL mapping schemes."""

    id: str
    agency: str
    names: Sequence[FusionString] = ()
    items: Sequence[FusionVtlMapping] = ()
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    isPartial: bool = False

    def to_model(self) -> VtlMappingScheme:
        """Converts deserialized class to pysdmx model class."""
        items = [i.to_model() for i in self.items]
        return VtlMappingScheme(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            version=self.version,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            is_external_reference=self.isExternalReference,
            agency=self.agency,
            items=items,
            is_partial=self.isPartial,
        )


class FusionTransformation(Struct, frozen=True):
    """Fusion-JSON payload for VTL transformations."""

    id: str
    expression: str
    result: str
    isPersistent: bool
    names: Sequence[FusionString] = ()
    descriptions: Sequence[FusionString] = ()

    def to_model(self) -> Transformation:
        """Converts deserialized class to pysdmx model class."""
        return Transformation(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
            expression=self.expression,
            is_persistent=self.isPersistent,
            result=self.result,
        )


class FusionTransformationScheme(
    Struct, frozen=True, rename={"agency": "agencyId"}
):
    """Fusion-JSON payload for VTL transformation schemes."""

    id: str
    agency: str
    vtlVersion: str
    names: Sequence[FusionString] = ()
    items: Sequence[FusionTransformation] = ()
    vtlMappingScheme: Optional[str] = None
    namePersonalisationScheme: Optional[str] = None
    customTypeScheme: Optional[str] = None
    rulesetSchemes: Sequence[str] = ()
    userDefinedOperatorScheme: Sequence[str] = ()
    descriptions: Sequence[FusionString] = ()
    version: str = "1.0"
    isExternalReference: bool = False
    validFrom: Optional[datetime] = None
    validTo: Optional[datetime] = None
    isPartial: bool = False

    def to_model(
        self,
        custom_type_schemes: Sequence[FusionCustomTypeScheme],
        vtl_mapping_schemes: Sequence[FusionVtlMappingScheme],
        name_personalisation_schemes: Sequence[
            FusionNamePersonalisationScheme
        ],
        ruleset_schemes: Sequence[FusionRulesetScheme],
        user_defined_operator_schemes: Sequence[
            FusionUserDefinedOperatorScheme
        ],
    ) -> TS:
        """Converts deserialized class to pysdmx model class."""
        cts = [i.to_model() for i in custom_type_schemes]
        vms = [i.to_model() for i in vtl_mapping_schemes]
        nps = [i.to_model() for i in name_personalisation_schemes]
        rss = [i.to_model() for i in ruleset_schemes]
        dos = [i.to_model() for i in user_defined_operator_schemes]
        items = [i.to_model() for i in self.items]
        return TS(
            self.id,
            name=self.names[0].value,
            description=(
                self.descriptions[0].value if self.descriptions else None
            ),
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
        )


class FusionVtlTransformationsMessage(Struct, frozen=True):
    """Fusion-JSON payload for /transformationscheme queries."""

    TransformationScheme: Sequence[FusionTransformationScheme]
    CustomTypeScheme: Sequence[FusionCustomTypeScheme] = ()
    VtlMappingScheme: Sequence[FusionVtlMappingScheme] = ()
    NamePersonalisationScheme: Sequence[FusionNamePersonalisationScheme] = ()
    RulesetScheme: Sequence[FusionRulesetScheme] = ()
    UserDefinedOperatorScheme: Sequence[FusionUserDefinedOperatorScheme] = ()

    def to_model(self) -> TS:
        """Converts deserialized class to pysdmx model class."""
        return self.TransformationScheme[0].to_model(
            self.CustomTypeScheme,
            self.VtlMappingScheme,
            self.NamePersonalisationScheme,
            self.RulesetScheme,
            self.UserDefinedOperatorScheme,
        )
