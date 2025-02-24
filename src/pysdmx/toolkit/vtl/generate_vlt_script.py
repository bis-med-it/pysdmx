"""Generates the full VTL Transformation Scheme script."""

from pysdmx.model import TransformationScheme
from pysdmx.toolkit.vtl.model_validations import model_validations


def generate_vtl_script(
    transformation_scheme: TransformationScheme, model_validation: bool = True
) -> str:
    """Generates the full VTL Transformation Scheme script."""
    if model_validation:
        model_validations(transformation_scheme)

    vtl_script = """""".strip()

    for ruleset_scheme in transformation_scheme.ruleset_schemes:
        for ruleset in ruleset_scheme.items:
            vtl_script += f"{ruleset.ruleset_definition}\n"
    for udo_scheme in transformation_scheme.user_defined_operator_schemes:
        for udo in udo_scheme.items:
            vtl_script += f"{udo.operator_definition}\n"
    for transformation in transformation_scheme.items:
        vtl_script += f"{transformation.full_expression}\n"

    return vtl_script
