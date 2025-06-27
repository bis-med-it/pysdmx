"""Private module for VTL validation functions."""

from vtlengine.API import create_ast  # type: ignore[import-untyped]
from vtlengine.AST import (  # type: ignore[import-untyped]
    DPRuleset as ASTDPRuleset,
)
from vtlengine.AST import HRuleset as ASTHRuleset
from vtlengine.AST import (
    Operator as ASTOperator,
)

from pysdmx.errors import Invalid
from pysdmx.io.xml.__tokens import RULE_SCHEME, UDO_SCHEME
from pysdmx.model import Reference
from pysdmx.model.vtl import (
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
)


def _ruleset_validation(ruleset: Ruleset) -> None:
    """Additional validation checks for rulesets."""
    try:
        ast = create_ast(ruleset.ruleset_definition)
    except Exception as e:
        raise Invalid(f"Invalid ruleset definition: {str(e)}") from e
    if len(ast.children) > 1:
        raise Invalid("A single RulesetDefinition is valid in a Ruleset")
    if ruleset.ruleset_type == "hierarchical" and not isinstance(
        ast.children[0], ASTHRuleset
    ):
        raise Invalid("Ruleset type does not match the definition")
    if ruleset.ruleset_type == "datapoint" and not isinstance(
        ast.children[0], ASTDPRuleset
    ):
        raise Invalid("Ruleset type does not match the definition")
    if (
        ruleset.ruleset_scope == "variable"
        and ast.children[0].signature_type != "variable"
    ):
        raise Invalid("Ruleset scope does not match the definition")
    if (
        ruleset.ruleset_scope == "valuedomain"
        and ast.children[0].signature_type != "valuedomain"
    ):
        raise Invalid("Ruleset scope does not match the definition")


def _ruleset_scheme_validations(ruleset_scheme: RulesetScheme) -> None:
    """Additional validation checks for ruleset schemes."""
    if not ruleset_scheme.items:
        raise Invalid("RulesetScheme must contain at least one Ruleset")
    for ruleset in ruleset_scheme.items:
        if not isinstance(ruleset, Ruleset):
            raise Invalid("RulesetScheme must contain Ruleset items")
        _ruleset_validation(ruleset)


def _ruleset_scheme_reference_validations(ruleset_scheme: Reference) -> None:
    """Additional validation checks for ruleset schemes."""
    if ruleset_scheme.sdmx_type != RULE_SCHEME:
        raise Invalid(
            "Reference in Ruleset Schemes must point to a Ruleset Scheme, "
            f"got {ruleset_scheme.sdmx_type}"
        )


def _user_defined_operator_validation(udo: UserDefinedOperator) -> None:
    """Additional validation checks for user defined operators."""
    try:
        ast = create_ast(udo.operator_definition)
    except Exception as e:
        raise Invalid(f"Invalid operator definition: {str(e)}") from e
    if len(ast.children) > 1:
        raise Invalid(
            "A single OperatorDefinition is valid in a UserDefinedOperator"
        )
    if not isinstance(ast.children[0], ASTOperator):
        raise Invalid(
            "User defined operator type does not match the definition"
        )


def _user_defined_operator_scheme_validations(
    udo_scheme: UserDefinedOperatorScheme,
) -> None:
    """Additional validation checks for user defined operator schemes."""
    if not udo_scheme.items:
        raise Invalid(
            "UserDefinedOperatorScheme must contain at least one "
            "UserDefinedOperator"
        )
    for udo in udo_scheme.items:
        if not isinstance(udo, UserDefinedOperator):
            raise Invalid(
                "UserDefinedOperatorScheme must contain UserDefinedOperator "
                "items"
            )
        _user_defined_operator_validation(udo)


def _udo_scheme_reference_validations(udo_scheme: Reference) -> None:
    """Additional validation checks for ruleset schemes."""
    if udo_scheme.sdmx_type != UDO_SCHEME:
        raise Invalid(
            "Reference in User Defined Operator Schemes"
            " must point to a Defined Operator Scheme, "
            f"got {udo_scheme.sdmx_type}"
        )


def _transformation_validations(transformation: Transformation) -> None:
    """Additional validation checks for transformations."""
    try:
        ast = create_ast(transformation.full_expression)
    except Exception as e:
        raise Invalid(f"Invalid transformation definition: {str(e)}") from e
    if len(ast.children) > 1:
        raise Invalid("A single Assignment is valid in a Transformation")


def _transformation_scheme_validations(
    transformation_scheme: TransformationScheme,
) -> None:
    """Additional validation checks for transformation schemes."""
    if not transformation_scheme.items:
        raise Invalid(
            "TransformationScheme must contain at least one Transformation"
        )

    for ruleset_scheme in transformation_scheme.ruleset_schemes:
        if isinstance(ruleset_scheme, RulesetScheme):
            _ruleset_scheme_validations(ruleset_scheme)
        if isinstance(ruleset_scheme, Reference):
            _ruleset_scheme_reference_validations(ruleset_scheme)
    for udo_scheme in transformation_scheme.user_defined_operator_schemes:
        if isinstance(udo_scheme, UserDefinedOperatorScheme):
            _user_defined_operator_scheme_validations(udo_scheme)
        if isinstance(udo_scheme, Reference):
            _udo_scheme_reference_validations(udo_scheme)
    for transformation in transformation_scheme.items:
        if not isinstance(transformation, Transformation):
            raise Invalid(
                "TransformationScheme must contain Transformation items"
            )
        _transformation_validations(transformation)
