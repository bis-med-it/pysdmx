"""Model validations for VTL models."""

from typing import Union

from pysdmx.errors import Invalid
from pysdmx.model import (
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlScheme,
)
from pysdmx.model.__base import Item
from pysdmx.toolkit.vtl.validations import (
    _ruleset_scheme_validations,
    _ruleset_validation,
    _transformation_scheme_validations,
    _transformation_validations,
    _user_defined_operator_scheme_validations,
    _user_defined_operator_validation,
)


def model_validations(model_obj: Union[VtlScheme, Item]) -> None:
    """Validation checks for VTL models."""
    if not isinstance(
        model_obj,
        (
            RulesetScheme,
            Ruleset,
            UserDefinedOperatorScheme,
            UserDefinedOperator,
            TransformationScheme,
            Transformation,
        ),
    ):
        raise Invalid("Invalid model object")

    if isinstance(model_obj, Ruleset):
        _ruleset_validation(model_obj)
    elif isinstance(model_obj, RulesetScheme):
        _ruleset_scheme_validations(model_obj)
    elif isinstance(model_obj, UserDefinedOperator):
        _user_defined_operator_validation(model_obj)
    elif isinstance(model_obj, UserDefinedOperatorScheme):
        _user_defined_operator_scheme_validations(model_obj)
    elif isinstance(model_obj, Transformation):
        _transformation_validations(model_obj)
    elif isinstance(model_obj, TransformationScheme):
        _transformation_scheme_validations(model_obj)
