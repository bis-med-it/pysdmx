"""Model for VTL artefacts."""

from enum import Enum
from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.errors import Invalid
from pysdmx.model.__base import Item, ItemScheme


class Transformation(Item, frozen=True, omit_defaults=True):
    """A statement which assigns the outcome of an expression to a result.

    Attributes:
        expression: str.
          The expression bound to the Transformation (no semicolon).
        result: str.
          The Dataset or Scalar name where we store the result.
        is_persistent: bool = False.
          If the result is persistent.
    """

    expression: str = ""
    is_persistent: bool = False
    result: str = ""

    @property
    def full_expression(self) -> str:
        """Return the full expression with the semicolon."""
        if self.is_persistent:
            assign_operand = "<-"
        else:
            assign_operand = ":="

        return f"{self.result} {assign_operand} {self.expression};"


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


class _VTLVersionEnum(Enum):
    """Enumeration of VTL versions."""

    VTL_1_0 = "1.0"
    VTL_2_0 = "2.0"
    VTL_2_1 = "2.1"


class VtlScheme(ItemScheme, frozen=True, omit_defaults=True):
    """A VTL item scheme with the additional propery 'vtl_version'."""

    vtl_version: Optional[str] = None

    def __post_init__(self) -> None:
        """Additional validation checks for VTL item schemes.

        Version must be a valid VTL version.

        Raises:
            Invalid: If the version is not a valid VTL version
        """
        if self.vtl_version not in _VTLVersionEnum._value2member_map_:
            raise Invalid(f"Invalid VTL version: {self.vtl_version}")


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
    ruleset_schemes: Sequence[str] = ()


class VtlMappingScheme(ItemScheme, frozen=True, omit_defaults=True):
    """A collection of VTL mappings."""


class TransformationScheme(VtlScheme, frozen=True, omit_defaults=True):
    """VTL Transformation Scheme class.

    TransformationScheme is a set of Transformations aimed at getting some
    meaningful results for the user
    (e.g. the validation of one or more Data Sets).

    This set of Transformations is meant to be executed together
    (in the same run) and may contain any number of Transformations to
    produce any number of results.
    Therefore, a TransformationScheme can be considered as a VTL program.

    The TransformationScheme must include the attribute vtlVersion expressed as
    a string (e.g. “2.0”), as the version of the VTL determines which syntax
    is used in defining the transformations of the scheme.
    This attribute is inherited from the VTLItemScheme class.

    Attributes:
        vtl_mapping_scheme: Optional[VtlMappingScheme].
          The VTL mapping scheme.
        name_personalisation_scheme: Optional[NamePersonalisationScheme].
          The name personalisation scheme.
        custom_type_scheme: Optional[CustomTypeScheme].
          The custom type scheme.
        ruleset_schemes: Sequence[RulesetScheme].
          The ruleset schemes.
        user_defined_operator_schemes: Sequence[UserDefinedOperatorScheme].
          The user-defined operator schemes.
    """

    vtl_mapping_scheme: Optional[VtlMappingScheme] = None
    name_personalisation_scheme: Optional[NamePersonalisationScheme] = None
    custom_type_scheme: Optional[CustomTypeScheme] = None
    ruleset_schemes: Sequence[RulesetScheme] = ()
    user_defined_operator_schemes: Sequence[UserDefinedOperatorScheme] = ()
