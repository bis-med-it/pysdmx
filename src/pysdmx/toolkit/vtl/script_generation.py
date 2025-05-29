"""Generates the full VTL Transformation Scheme script."""

from typing import Sequence, Union

from pysdmx.__extras_check import __check_vtl_extra
from pysdmx.model import (
    Reference,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperatorScheme,
)


def _process_ruleset_scheme(
    ruleset_schemes: Sequence[Union[RulesetScheme, Reference]],
) -> str:
    """Processes the Ruleset Scheme objects and returns the VTL script."""
    vtl_script = ""
    for ruleset_scheme in ruleset_schemes:
        if isinstance(ruleset_scheme, RulesetScheme):
            for ruleset in ruleset_scheme.items:
                vtl_script += f"{ruleset.ruleset_definition}\n"

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

    return vtl_script


def _process_transformation(transformations: Sequence[Transformation]) -> str:
    """Processes the transformation objects and returns the VTL script."""
    vtl_script = ""
    for transformation in transformations:
        vtl_script += f"{transformation.full_expression}\n"

    return vtl_script


def generate_vtl_script(
    transformation_scheme: TransformationScheme,
    model_validation: bool = False,
    prettyprint: bool = False,
) -> str:
    """Generates the VTL script from a TransformationScheme.

    This method iterates over the TransformationScheme object and its referred
    RulesetSchemes and UserDefinedOperatorSchemes to generate the VTL script
    as string

    The model_validation feature checks if the model object is valid by
    parsing the VTL code inside the definitions.

    The prettyprint feature formats the VTL script in a user-friendly way.

    .. important::
        The prettyprint and model_validation features require
        the pysdmx[vtl] extra.

    Args:
        transformation_scheme: A TransformationScheme object.
        model_validation: A boolean value to check if the model
                        object is valid.
                        if True, the model object is validated.
        prettyprint: A boolean value to check if the generated script
                     is returned formatted.

    Returns:
        A string containing the full VTL Transformation Scheme script.

    """
    if model_validation:
        __check_vtl_extra()
        from pysdmx.toolkit.vtl.validation import model_validations

        model_validations(transformation_scheme)

    vtl_script = ""

    vtl_script += _process_ruleset_scheme(
        transformation_scheme.ruleset_schemes
    )
    vtl_script += _process_udo_scheme(
        transformation_scheme.user_defined_operator_schemes
    )
    vtl_script += _process_transformation(transformation_scheme.items)

    if prettyprint:
        __check_vtl_extra()
        from vtlengine import prettify  # type: ignore[import-untyped]

        return prettify(vtl_script)

    return vtl_script
