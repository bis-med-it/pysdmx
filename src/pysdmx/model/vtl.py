"""Model for VTL artefacts."""

from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.model.__base import Item, ItemScheme


class Transformation(Item, frozen=True, omit_defaults=True):
    """A statement which assigns the outcome of an expression to a result."""

    expression: str = ""
    is_persistent: bool = False
    result: str = ""


class Ruleset(Item, frozen=True, omit_defaults=True):
    """A persistent set of rules."""

    ruleset_definition: str = ""
    ruleset_scope: str = ""
    ruleset_type: str = ""


class UserDefinedOperator(Item, frozen=True, omit_defaults=True):
    """Custom VTL operator that extends the VTL standard library."""

    operator_definition: str = ""


class NamePersonalisation(Item, frozen=True, omit_defaults=True):
    """Definition of personalised name."""

    personalised_name: str = ""
    vtl_artefact: str = ""
    vtl_default_name: str = ""


class VtlMapping(Item, frozen=True, omit_defaults=True):
    """Single VTL mapping."""


class ToVtlMapping(Struct, frozen=True, omit_defaults=True):
    """The mapping method and filter used when mapping from SDMX to VTL."""

    to_vtl_sub_space: Sequence[str] = ()
    method: Optional[str] = None


class FromVtlMapping(Struct, frozen=True, omit_defaults=True):
    """The mapping method and filter used when mapping from VTL to SDMX."""

    from_vtl_sub_space: Sequence[str] = ()
    method: Optional[str] = None


class VtlDataflowMapping(VtlMapping, frozen=True, omit_defaults=True):
    """Single mapping with a dataflow."""

    dataflow: str = ""
    dataflow_alias: str = ""
    to_vtl_mapping_method: Optional[ToVtlMapping] = None
    from_vtl_mapping_method: Optional[FromVtlMapping] = None


class VtlCodelistMapping(VtlMapping, frozen=True, omit_defaults=True):
    """Single mapping with a codelist."""

    codelist: str = ""
    codelist_alias: str = ""


class VtlConceptMapping(VtlMapping, frozen=True, omit_defaults=True):
    """Single mapping with a concept."""

    concept: str = ""
    concept_alias: str = ""


class CustomType(Item, frozen=True, omit_defaults=True):
    """Custom specification for a VTL basic scalar type."""

    data_type: str = ""
    null_value: Optional[str] = None
    output_format: Optional[str] = None
    vtl_literal_format: Optional[str] = None
    vtl_scalar_type: str = ""


class VtlScheme(ItemScheme, frozen=True, omit_defaults=True):
    """A VTL item scheme with the additional propery 'vtl_version'."""

    vtl_version: Optional[str] = None


class CustomTypeScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of custom specifications for VTL basic scalar types."""


class NamePersonalisationScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of name personalisations."""


class RulesetScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of rulesets."""

    vtl_mapping_scheme: Optional[str] = None


class UserDefinedOperatorScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of user-defined operators."""

    vtl_mapping_scheme: Optional[str] = None
    ruleset_scheme: Optional[str] = None


class VtlMappingScheme(ItemScheme, frozen=True, omit_defaults=True):
    """A collection of VTL mappings."""


class TransformationScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of transformations meant to be executed together."""

    vtl_mapping_scheme: Optional[VtlMappingScheme] = None
    name_personalisation_scheme: Optional[NamePersonalisationScheme] = None
    custom_type_scheme: Optional[CustomTypeScheme] = None
    ruleset_schemes: Sequence[RulesetScheme] = ()
    user_defined_operator_schemes: Sequence[UserDefinedOperatorScheme] = None
