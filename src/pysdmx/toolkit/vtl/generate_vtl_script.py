"""Generates the full VTL Transformation Scheme script."""

from typing import Sequence, Union

from pysdmx.model import (
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperatorScheme,
)
from pysdmx.toolkit.vtl.model_validations import model_validations
from pysdmx.util import Reference


def _process_ruleset_scheme(
    ruleset_schemes: Sequence[Union[RulesetScheme, Reference]],
) -> str:
    """Processes the Ruleset Scheme objects and returns the VTL script."""
    vtl_script = ""
    for ruleset_scheme in ruleset_schemes:
        if isinstance(ruleset_scheme, RulesetScheme):
            for ruleset in ruleset_scheme.items:
                vtl_script += f"{ruleset.ruleset_definition}\n"
        if isinstance(ruleset_scheme, Reference):
            vtl_script += f"{ruleset_scheme}\n"

    return vtl_script


def _process_udo_scheme(
    udo_schemes: Sequence[Union[UserDefinedOperatorScheme, Reference]],
) -> str:
    """Processes the UDO Scheme objects and returns the VTL script."""
    vtl_script = ""
    for udo_scheme in udo_schemes:
        if isinstance(udo_scheme, UserDefinedOperatorScheme):
            for udo in udo_scheme.items:
                vtl_script += f"{udo.operator_definition}\n"
        if isinstance(udo_scheme, Reference):
            vtl_script += f"{udo_scheme}\n"

    return vtl_script


def _process_transformation(transformations: Sequence[Transformation]) -> str:
    """Processes the transformation objects and returns the VTL script."""
    vtl_script = ""
    for transformation in transformations:
        vtl_script += f"{transformation.full_expression}\n"

    return vtl_script


def generate_vtl_script(
    transformation_scheme: TransformationScheme, model_validation: bool = True
) -> str:
    """Generates the full VTL Transformation Scheme script.

    Args:
        transformation_scheme: A TransformationScheme object.
        model_validation: A boolean value to check if the model
                        object is valid.
                        if True, the model object is validated.

    returns:
        A string containing the full VTL Transformation Scheme script.

    """
    if model_validation:
        model_validations(transformation_scheme)

    vtl_script = ""

    vtl_script += _process_ruleset_scheme(
        transformation_scheme.ruleset_schemes
    )
    vtl_script += _process_udo_scheme(
        transformation_scheme.user_defined_operator_schemes
    )
    vtl_script += _process_transformation(transformation_scheme.items)

    return vtl_script
