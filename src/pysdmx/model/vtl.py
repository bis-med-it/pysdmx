"""Model for VTL artefacts."""

from enum import Enum
from typing import Optional, Sequence, Literal

from msgspec import Struct
from vtlengine.API import create_ast  # type: ignore[import-untyped]
from vtlengine.AST import DPRuleset as ASTDPRuleset, HRuleset as ASTHRuleset  # type: ignore[import-untyped]
from vtlengine.AST import Operator as ASTOperator  # type: ignore[import-untyped]

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

    def __post_init__(self) -> None:
        try:
            ast = create_ast(self.full_expression)
        except Exception as e:
            raise Invalid(f"Invalid transformation definition: {str(e)}") from e
        if isinstance(ast.children[0], ASTOperator) or isinstance(ast.children[0], ASTDPRuleset) or isinstance(
                ast.children[0], ASTHRuleset):
            raise Invalid("Invalid transformation definition")

    @property
    def full_expression(self) -> str:
        """Return the full expression with the semicolon."""
        assign_operand = "<-" if self.is_persistent else ":="
        full_expression = f"{self.result} {assign_operand} {self.expression}"
        return full_expression if full_expression.strip().endswith(";") else f"{full_expression};"


class Ruleset(Item, frozen=True, omit_defaults=True):
    """A persistent set of rules."""

    ruleset_definition: str = ""
    ruleset_scope: Optional[Literal["variable", "valuedomain"]] = None
    ruleset_type: Optional[Literal["datapoint", "hierarchical"]] = None

    def __post_init__(self) -> None:
        try:
            ast = create_ast(self.ruleset_definition)
        except Exception as e:
            raise Invalid(f"Invalid ruleset definition: {str(e)}") from e
        if self.ruleset_type == "hierarchical" and not isinstance(ast.children[0], ASTHRuleset):
            raise Invalid("Invalid ruleset definition")
        if self.ruleset_type == "datapoint" and not isinstance(ast.children[0], ASTDPRuleset):
            raise Invalid("Invalid ruleset definition")
        if self.ruleset_scope == "variable" and ast.children[0].__getattribute__("signature_type") != "variable":
            raise Invalid("Invalid ruleset definition")
        if self.ruleset_scope == "valuedomain" and ast.children[0].__getattribute__("signature_type") != "valuedomain":
            raise Invalid("Invalid ruleset definition")


class UserDefinedOperator(Item, frozen=True, omit_defaults=True):
    """Custom VTL operator that extends the VTL standard library."""

    operator_definition: str = ""

    def __post_init__(self) -> None:
        try:
            ast = create_ast(self.operator_definition)
        except Exception as e:
            raise Invalid(f"Invalid operator definition: {str(e)}") from e
        if not isinstance(ast.children[0], ASTOperator):
            raise Invalid("Invalid operator definition")


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
    items: Sequence[Ruleset] = ()


class UserDefinedOperatorScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of user-defined operators."""

    vtl_mapping_scheme: Optional[str] = None
    ruleset_schemes: Sequence[str] = ()
    items: Sequence[UserDefinedOperator] = ()


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
    items: Sequence[Transformation] = ()

    def generate_vtl_script(self, syntax_validation: bool = True) -> str:
        """Generates the full VTL Transformation Scheme script."""
        vtl_script = """""".strip()

        for ruleset_scheme in self.ruleset_schemes:
            for ruleset in ruleset_scheme.items:
                vtl_script += f"{ruleset.ruleset_definition}\n"

        for udo_scheme in self.user_defined_operator_schemes:
            for udo in udo_scheme.items:
                vtl_script += f"{udo.operator_definition}\n"

        for transformation in self.items:
            vtl_script += f"{transformation.full_expression}\n"

        syntax_validator(vtl_script)

        return vtl_script


def syntax_validator(script: str) -> None:
    """Validates the VTL script syntax."""
    try:
        create_ast(script)
    except Exception as e:
        raise ValueError(f"The syntax is invalid: {str(e)}") from e
