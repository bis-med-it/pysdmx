"""VTL (Validation Transformation Language) model classes."""

from enum import Enum

from pysdmx.errors import Invalid
from pysdmx.model.__base import Item, ItemScheme


class _VTLVersionEnum(Enum):
    """Enumeration of VTL versions."""

    VTL_1_0 = "1.0"
    VTL_2_0 = "2.0"
    VTL_2_1 = "2.1"


class VTLItemScheme(ItemScheme, frozen=True, omit_defaults=True, kw_only=True):
    """Superclass for VTL item schemes.

    Not part of the SDMX Information Model.
    Used only to provide a common interface for VTL items scheme
    and not duplicating post_init checks.

    Attributes:
        vtlVersion: str.
          The version of the VTL used.
    """

    vtlVersion: str

    def __post_init__(self) -> None:
        """Additional validation checks for VTL item schemes.

        Version must be a valid VTL version.

        Raises:
            Invalid: If the version is not a valid VTL version
        """
        if self.vtlVersion not in _VTLVersionEnum._value2member_map_:
            raise Invalid(f"Invalid VTL version: {self.vtlVersion}")


# Transformations
class TransformationScheme(VTLItemScheme, frozen=True, kw_only=True):
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
    """

    pass


class Transformation(Item, frozen=True, omit_defaults=True, kw_only=True):
    """VTL Transformation class.

    Attributes:
        Expression: str.
          The expression bound to the Transformation (no semicolon).
        Result: str.
          The Dataset or Scalar name where we store the result.
        isPersistent: bool = False. If the result is persistent.
    """

    Expression: str
    Result: str
    isPersistent: bool = False

    @property
    def full_expression(self) -> str:
        """Return the full expression with the semicolon."""
        if self.isPersistent:
            assign_operand = "<-"
        else:
            assign_operand = ":="

        return f"{self.Result} {assign_operand} {self.Expression};"

    # TODO: Use VTL Engine for syntax/semantic validation based on VTL?


# UDOs
class UserDefinedOperatorScheme(VTLItemScheme, frozen=True, kw_only=True):
    """VTL User Defined Operator Scheme class.

    The UserDefinedOperatorScheme is a container for zero of more
    UserDefinedOperator.

    The UserDefinedOperatorScheme must include the attribute
    vtlVersion expressed as a string (e.g. “2.0”), as the version of
    the VTL determines which syntax is used in defining
    the User Defined Operators of the Scheme.
    This attribute is inherited from the VTLItemScheme class.
    """

    pass


class UserDefinedOperator(Item, frozen=True, omit_defaults=True, kw_only=True):
    """VTL User Defined Operator class.

    The UserDefinedOperator is defined using VTL standard
    operators. This is essential for understanding the actual behaviour of the
    Transformations that invoke them.

    Attributes:
        operatorDefinition: str.
          VTL statement that defines the operator according to the syntax
          of the VTL definition language.
    """

    operatorDefinition: str

    # TODO: Use VTL Engine for syntax/semantic validation based on VTL?


# Ruleset
class RulesetScheme(VTLItemScheme, frozen=True, kw_only=True):
    """VTL Ruleset Scheme class.

    The RulesetScheme is a container for zero or more Ruleset.

    The RulesetScheme must include the attribute vtlVersion expressed as a
    string (e.g. “2.0”), as the version of the VTL determines which syntax
    is used in defining the Rulesets of the scheme.
    This attribute is inherited from the VTLItemScheme class.
    """

    pass


class _VTLRulesetTypeEnum(Enum):
    """Enumeration of VTL Ruleset types."""

    DATAPOINT = "datapoint"
    HIERARCHICAL = "hierarchical"


class Ruleset(Item, frozen=True, omit_defaults=True, kw_only=True):
    """VTL Ruleset class.

    A persistent set of rules which can be invoked by
    appropriate VTL operators.
    """

    rulesetDefinition: str
    rulesetScope: str
    rulesetType: str

    def __post_init__(self) -> None:
        """Additional validation checks for Ruleset.

        Raises:
            Invalid: If the rulesetType is not a valid VTL ruleset type
        """
        if self.rulesetType not in _VTLRulesetTypeEnum._value2member_map_:
            raise Invalid(f"Invalid VTL Ruleset type: {self.rulesetType}")

    # TODO: Use VTL Engine for syntax/semantic validation based on VTL?
