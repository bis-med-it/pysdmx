"""Model validations for VTL models."""

from typing import Optional, Sequence, Union

from pysdmx.__extras_check import __check_vtl_extra
from pysdmx.errors import Invalid
from pysdmx.model import (
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlExecution,
    VtlMappingScheme,
    VtlScheme,
)
from pysdmx.model.__base import Item, MaintainableArtefact


def model_validations(
    model_obj: Union[VtlScheme, Item, VtlMappingScheme, VtlExecution],
    structures: Optional[Sequence[MaintainableArtefact]] = None,
) -> None:
    """Validation checks for VTL objects.

    This method performs validation checks on VTLScheme objects ,
    such as TransformationScheme, RulesetScheme,
    UserDefinedOperatorScheme, etc. or its items,
    like Ruleset, Transformation, UserDefinedOperator, etc.

    It raises an Invalid exception if the model object is not valid.

    The definitions of rulesets and user defined operators are valid with
    or without the semicolon that ends a VTL statement.

    The model validation checks on items:

    * Ruleset validation

        * A single RulesetDefinition (define ...) is valid in a Ruleset

        * Ruleset type matches the definition (hierarchical, datapoint
          or viral, the latter for a viral propagation)

        * Ruleset scope matches the signature (variable or valuedomain)

    * User Defined Operator validation

        * A single OperatorDefinition (define operator ...)
          is valid in a User Defined Operator

    * Transformation validation

        * Checks if the transformation is valid

        * Checks a single assignment is present in the expression

    The model validation checks on VTLScheme:

    * All the schemes below, also when they are checked as part of a
      TransformationScheme

        * Checks if it has the VTL version, which is mandatory

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

        * Checks if these schemes have its VTL version

        * Checks if a variable or value domain has a single viral
          propagation in its RulesetSchemes

        * Checks its VtlMappingScheme (if any), and if each output of the
          VtlMappingScheme is the result of a persistent Transformation

    * VtlMappingScheme validation

        * Checks if all the mappings have a VTL alias

        * Checks if the alias of the codelist mappings has between 1 and
          128 characters, without white spaces or single quotes, and if
          they reference a codelist

    * VtlExecution validation

        * Checks if each data extraction references a VtlDatasetMapping of
          the VtlMappingScheme of its TransformationScheme that is an input

        * Checks if the context of a query extraction uses the data
          structure of the artefact of its VtlDatasetMapping

    The checks that involve other artefacts are made when these artefacts
    are available: because the object holds them, instead of a reference
    to them, or because they are among the structures.

    Args:
        model_obj: A VTLScheme, VtlMappingScheme, VtlExecution or Item object.
        structures: The artefacts referenced by the object, e.g. the
            structures of the message it belongs to.
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

        _transformation_scheme_validations(model_obj, structures or ())
    elif isinstance(model_obj, VtlMappingScheme):
        from pysdmx.toolkit.vtl._validations import (
            _vtl_mapping_scheme_validations,
        )

        _vtl_mapping_scheme_validations(model_obj)
    elif isinstance(model_obj, VtlExecution):
        from pysdmx.toolkit.vtl._validations import (
            _vtl_execution_validations,
        )

        _vtl_execution_validations(model_obj, structures or ())
    else:
        raise Invalid("Invalid model object")
