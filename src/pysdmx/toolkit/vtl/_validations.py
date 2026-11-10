"""Private module for VTL validation functions."""

from typing import Any, List, Optional, Sequence, Type, TypeVar, cast

from vtlengine.API import create_ast
from vtlengine.AST import DPRuleset as ASTDPRuleset
from vtlengine.AST import HRuleset as ASTHRuleset
from vtlengine.AST import Operator as ASTOperator
from vtlengine.AST import ViralPropagationDef as ASTViralPropagation

from pysdmx.errors import Invalid
from pysdmx.model import Reference
from pysdmx.model.dataflow import Dataflow, ProvisionAgreement
from pysdmx.model.vtl import (
    _VTL_ALIAS,
    Ruleset,
    RulesetScheme,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlCodelistMapping,
    VtlDatasetMapping,
    VtlExecution,
    VtlMappingScheme,
    VtlScheme,
    _short_urn,
)
from pysdmx.toolkit.vtl.script_generation import _with_semicolon

T = TypeVar("T")


def _short(artefact: Any) -> Optional[str]:
    """Returns the short URN of an artefact, a reference or a URN."""
    short_urn = _short_urn(artefact)
    if short_urn is None and isinstance(artefact, str):
        return artefact
    return short_urn


def _find(ref: Any, structures: Sequence[Any], type_: Type[T]) -> Optional[T]:
    """Returns a referenced artefact, if given or among the structures."""
    if isinstance(ref, type_):
        return ref
    short_urn = _short(ref)
    return next(
        (
            s
            for s in structures
            if isinstance(s, type_) and _short(s) == short_urn
        ),
        None,
    )


def _data_structure(artefact: Any, structures: Sequence[Any]) -> Optional[str]:
    """Returns the short URN of the data structure of an artefact, if known.

    The artefact is a data structure, or a dataflow or provision agreement
    using it.
    """
    short_urn = _short(artefact) or ""
    if short_urn.startswith("DataStructure="):
        return short_urn
    if short_urn.startswith("ProvisionAgreement="):
        agreement = _find(artefact, structures, ProvisionAgreement)
        return (
            _data_structure(agreement.dataflow, structures)
            if agreement
            else None
        )
    dataflow = _find(artefact, structures, Dataflow)
    return (
        _data_structure(dataflow.structure, structures) if dataflow else None
    )


def _ruleset_validation(ruleset: Ruleset) -> None:
    """Additional validation checks for rulesets."""
    try:
        ast = create_ast(_with_semicolon(ruleset.ruleset_definition))
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
    if ruleset.ruleset_type == "viral" and not isinstance(
        ast.children[0], ASTViralPropagation
    ):
        raise Invalid("Ruleset type does not match the definition")

    child = ast.children[0]
    signature_type = getattr(child, "signature_type", None)
    if ruleset.ruleset_scope == "variable" and signature_type != "variable":
        raise Invalid("Ruleset scope does not match the definition")
    if (
        ruleset.ruleset_scope == "valuedomain"
        and signature_type != "valuedomain"
    ):
        raise Invalid("Ruleset scope does not match the definition")


def _vtl_version_validation(scheme: VtlScheme) -> None:
    """Checks that a VTL scheme has the mandatory VTL version."""
    if scheme.vtl_version is None:
        raise Invalid(f"{type(scheme).__name__} must have a VTL version")


def _ruleset_scheme_validations(ruleset_scheme: RulesetScheme) -> None:
    """Additional validation checks for ruleset schemes."""
    _vtl_version_validation(ruleset_scheme)
    if not ruleset_scheme.items:
        raise Invalid("RulesetScheme must contain at least one Ruleset")
    for ruleset in ruleset_scheme.items:
        if not isinstance(ruleset, Ruleset):
            raise Invalid("RulesetScheme must contain Ruleset items")
        _ruleset_validation(ruleset)


def _ruleset_scheme_reference_validations(ruleset_scheme: Reference) -> None:
    """Additional validation checks for ruleset schemes."""
    if ruleset_scheme.sdmx_type != "RulesetScheme":
        raise Invalid(
            "Reference in Ruleset Schemes must point to a Ruleset Scheme, "
            f"got {ruleset_scheme.sdmx_type}"
        )


def _user_defined_operator_validation(udo: UserDefinedOperator) -> None:
    """Additional validation checks for user defined operators."""
    try:
        ast = create_ast(_with_semicolon(udo.operator_definition))
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
    _vtl_version_validation(udo_scheme)
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
    if udo_scheme.sdmx_type != "UserDefinedOperatorScheme":
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


def _vtl_mapping_scheme_validations(scheme: VtlMappingScheme) -> None:
    """Additional validation checks for VTL mapping schemes."""
    for mapping in scheme.items:
        if not mapping.vtl_alias:
            raise Invalid(
                f"The VTL mapping {mapping.id} must have a VTL alias"
            )
        if not isinstance(mapping, VtlCodelistMapping):
            continue
        if not _VTL_ALIAS.fullmatch(mapping.vtl_alias):
            raise Invalid(
                f"The VTL alias of the mapping {mapping.id} must have "
                "between 1 and 128 characters, without white spaces or "
                "single quotes"
            )
        if not (_short(mapping.codelist) or "").startswith("Codelist="):
            raise Invalid(
                f"The VTL mapping {mapping.id} must reference a codelist"
            )


def _viral_propagations_validation(schemes: Sequence[RulesetScheme]) -> None:
    """Checks that a variable or value domain has one viral propagation."""
    targets = set()
    for scheme in schemes:
        for ruleset in scheme.items:
            if ruleset.ruleset_type != "viral":
                continue
            definition = cast(
                ASTViralPropagation,
                create_ast(
                    _with_semicolon(ruleset.ruleset_definition)
                ).children[0],
            )
            target = f"{definition.signature_type} {definition.target}"
            if target in targets:
                raise Invalid(
                    "A TransformationScheme must have a single viral "
                    f"propagation for the {target}"
                )
            targets.add(target)


def _outputs_validation(
    scheme: TransformationScheme, mappings: VtlMappingScheme
) -> None:
    """Checks that the outputs are results of persistent transformations."""
    persistent = {
        t.result.strip().strip("'") for t in scheme.items if t.is_persistent
    }
    for mapping in mappings.items:
        if (
            isinstance(mapping, VtlDatasetMapping)
            and not mapping.is_input
            and mapping.vtl_alias not in persistent
        ):
            raise Invalid(
                f"The output {mapping.vtl_alias} of the VTL mapping scheme "
                f"{mappings.id} must be the result of a persistent "
                "Transformation"
            )


def _referenced_schemes(
    scheme: TransformationScheme,
    references: Sequence[Any],
    structures: Sequence[Any],
    type_: Type[T],
) -> List[T]:
    """Returns the schemes of a transformation scheme that are available.

    The references to the other ones must be of the right class.
    """
    found = []
    for reference in references:
        referenced = _find(reference, structures, type_)
        if referenced is not None:
            version = referenced.vtl_version  # type: ignore[attr-defined]
            if version is not None and version != scheme.vtl_version:
                raise Invalid(
                    f"{type_.__name__} must have the VTL version of the "
                    "TransformationScheme that references it"
                )
            found.append(referenced)
        elif type_ is RulesetScheme:
            _ruleset_scheme_reference_validations(reference)
        else:
            _udo_scheme_reference_validations(reference)
    return found


def _transformation_scheme_validations(
    transformation_scheme: TransformationScheme,
    structures: Sequence[Any] = (),
) -> None:
    """Additional validation checks for transformation schemes."""
    _vtl_version_validation(transformation_scheme)
    if not transformation_scheme.items:
        raise Invalid(
            "TransformationScheme must contain at least one Transformation"
        )

    ruleset_schemes = _referenced_schemes(
        transformation_scheme,
        transformation_scheme.ruleset_schemes,
        structures,
        RulesetScheme,
    )
    for ruleset_scheme in ruleset_schemes:
        _ruleset_scheme_validations(ruleset_scheme)
    _viral_propagations_validation(ruleset_schemes)
    for udo_scheme in _referenced_schemes(
        transformation_scheme,
        transformation_scheme.user_defined_operator_schemes,
        structures,
        UserDefinedOperatorScheme,
    ):
        _user_defined_operator_scheme_validations(udo_scheme)
    for transformation in transformation_scheme.items:
        if not isinstance(transformation, Transformation):
            raise Invalid(
                "TransformationScheme must contain Transformation items"
            )
        _transformation_validations(transformation)

    reference = transformation_scheme.vtl_mapping_scheme
    mappings = _find(reference, structures, VtlMappingScheme)
    if mappings is not None:
        _vtl_mapping_scheme_validations(mappings)
        _outputs_validation(transformation_scheme, mappings)
    elif (
        isinstance(reference, Reference)
        and reference.sdmx_type != "VtlMappingScheme"
    ):
        raise Invalid(
            "The VTL mapping scheme of a TransformationScheme must be a "
            f"VTL Mapping Scheme, got {reference.sdmx_type}"
        )


def _vtl_execution_validations(
    execution: VtlExecution, structures: Sequence[Any] = ()
) -> None:
    """Additional validation checks for VTL executions.

    They need the transformation scheme of the execution and its VTL
    mapping scheme, given in the execution or among the structures.
    """
    scheme = _find(
        execution.transformation_scheme, structures, TransformationScheme
    )
    mappings = (
        _find(scheme.vtl_mapping_scheme, structures, VtlMappingScheme)
        if scheme
        else None
    )
    if mappings is None:
        return
    prefix = f"VtlDatasetMapping={mappings.short_urn.split('=', 1)[1]}."
    datasets = {
        m.id: m for m in mappings.items if isinstance(m, VtlDatasetMapping)
    }
    for extraction in execution.extractions:
        urn = str(_short_urn(extraction.dataset_mapping))
        mapping = (
            datasets.get(urn[len(prefix) :])
            if urn.startswith(prefix)
            else None
        )
        if mapping is None:
            raise Invalid(
                f"The data extraction of {urn} does not apply to a VTL "
                "Data Set of the executed program"
            )
        if not mapping.is_input:
            raise Invalid(
                f"The data extraction of {urn} is not valid, as the data "
                "extractions apply only to the inputs"
            )
        context = getattr(extraction, "context", None)
        expected = _data_structure(mapping.sdmx_artefact, structures)
        actual = _data_structure(context, structures)
        if expected and actual and expected != actual:
            raise Invalid(
                f"The data of the context of the data extraction of {urn} "
                "do not have the data structure of the VTL Data Set"
            )
