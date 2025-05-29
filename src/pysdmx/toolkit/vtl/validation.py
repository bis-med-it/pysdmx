"""Model validations for VTL models."""

from typing import Union

from pysdmx.__extras_check import __check_vtl_extra
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


def model_validations(model_obj: Union[VtlScheme, Item]) -> None:
    """Validation checks for VTL objects.

    This method performs validation checks on VTLScheme objects ,
    such as TransformationScheme, RulesetScheme,
    UserDefinedOperatorScheme, etc. or its items,
    like Ruleset, Transformation, UserDefinedOperator, etc.

    It raises an Invalid exception if the model object is not valid.

    The model validation checks on items:

    * Ruleset validation

        * A single RulesetDefinition (define ...) is valid in a Ruleset

        * Ruleset type matches the definition (hierarchical or datapoint)

        * Ruleset scope matches the signature (variable or valuedomain)

    * User Defined Operator validation

        * A single OperatorDefinition (define operator ...)
          is valid in a User Defined Operator

    * Transformation validation

        * Checks if the transformation is valid

        * Checks a single assignment is present in the expression

    The model validation checks on VTLScheme:

    * RulesetScheme validation

        * Checks if it contains at least one Ruleset

        * Checks if all items in the scheme are Ruleset

    * UserDefinedOperatorScheme validation

        * Checks if it contains at least one UserDefinedOperator

        * Checks if all items in the scheme are UserDefinedOperator

    * TransformationScheme validation

        * Checks if it contains at least one Transformation

        * Checks if all items in the scheme are Transformation

        * Checks the referenced RulesetSchemes (if any)
          and UserDefinedOperatorSchemes (if any)

    Args:
        model_obj: A VTLScheme or Item object.
    raises:
        Invalid: Invalid model object if the model object is not valid.
    """
    # We add here the check for vtl extra and add the local imports to
    # prevent unhandled ImportError
    __check_vtl_extra()

    if isinstance(model_obj, Ruleset):
        from pysdmx.toolkit.vtl._validations import (
            _ruleset_validation,
        )

        _ruleset_validation(model_obj)
    elif isinstance(model_obj, RulesetScheme):
        from pysdmx.toolkit.vtl._validations import (
            _ruleset_scheme_validations,
        )

        _ruleset_scheme_validations(model_obj)
    elif isinstance(model_obj, UserDefinedOperator):
        from pysdmx.toolkit.vtl._validations import (
            _user_defined_operator_validation,
        )

        _user_defined_operator_validation(model_obj)
    elif isinstance(model_obj, UserDefinedOperatorScheme):
        from pysdmx.toolkit.vtl._validations import (
            _user_defined_operator_scheme_validations,
        )

        _user_defined_operator_scheme_validations(model_obj)
    elif isinstance(model_obj, Transformation):
        from pysdmx.toolkit.vtl._validations import (
            _transformation_validations,
        )

        _transformation_validations(model_obj)
    elif isinstance(model_obj, TransformationScheme):
        from pysdmx.toolkit.vtl._validations import (
            _transformation_scheme_validations,
        )

        _transformation_scheme_validations(model_obj)
    else:
        raise Invalid("Invalid model object")
