"""Model for VTL artefacts."""

import re
from enum import Enum
from typing import Any, Literal, Optional, Sequence, Union

from msgspec import Struct
from msgspec.structs import force_setattr

from pysdmx.errors import Invalid
from pysdmx.model import Codelist, Concept
from pysdmx.model.__base import (
    DataflowRef,
    Item,
    ItemReference,
    ItemScheme,
    MaintainableArtefact,
    Reference,
)
from pysdmx.model.dataflow import (
    Dataflow,
    DataStructureDefinition,
    ProvisionAgreement,
)

_URN_BASE = "urn:sdmx:org.sdmx.infomodel."
_URN = re.compile(r"^urn:sdmx:org\.sdmx\.infomodel\.[a-z]+\.(\w+=.+)$")
_MAINTAINABLE = re.compile(r"^\w+=[^:=]+:[^(]+\([^)]+\)$")
_ITEM = re.compile(r"^\w+=[^:=]+:[^(]+\([^)]+\)\..+$")
_PACKAGES = {
    "Codelist": "codelist",
    "Concept": "conceptscheme",
    "DataStructure": "datastructure",
    "Dataflow": "datastructure",
    "ProvisionAgreement": "registry",
    "TransformationScheme": "transformation",
    "ValueList": "codelist",
    "VtlDatasetMapping": "transformation",
}
# White space as in the SDMX schemas: space, tab, line feed, carriage return
_VTL_ALIAS = re.compile(r"[^ \t\n\r']{1,128}")
_PARAMETER_NAME = re.compile(r"[^ \t\n\r]+")
_SDMX_API_VERSION = re.compile(r"(0|[1-9]\d*)\.(0|[1-9]\d*)")


def _short_urn(artefact: Any) -> Optional[str]:
    """Returns the short URN of an artefact, a reference to it or its URN."""
    if isinstance(artefact, str):
        m = _URN.match(artefact)
        return m.group(1) if m else None
    if isinstance(artefact, (Reference, ItemReference)):
        return str(artefact)
    if isinstance(artefact, DataflowRef):
        return f"Dataflow={artefact.agency}:{artefact.id}({artefact.version})"
    if isinstance(artefact, MaintainableArtefact):
        return artefact.short_urn
    return None


def _urn(artefact: Any) -> Optional[str]:
    """Returns the URN of an artefact, a reference to it or its URN."""
    if isinstance(artefact, str):
        return artefact or None
    short_urn = _short_urn(artefact)
    if short_urn is None:
        # An item does not know the scheme it belongs to.
        return getattr(artefact, "urn", None)
    package = _PACKAGES.get(short_urn.split("=")[0])
    return f"{_URN_BASE}{package}.{short_urn}" if package else None


def _is_maintainable(artefact: Any, *classes: str) -> bool:
    """Whether an artefact, reference or URN is of one of the classes."""
    short_urn = _short_urn(artefact)
    return (
        short_urn is not None
        and _MAINTAINABLE.match(short_urn) is not None
        and short_urn.split("=")[0] in classes
    )


def _sync_alias(mapping: "VtlMapping", deprecated: str) -> None:
    """Gives the VTL alias and its deprecated counterpart the same value."""
    old = getattr(mapping, deprecated)
    new = mapping.vtl_alias
    if old and new and old != new:
        raise Invalid(
            "Invalid VTL mapping",
            f"The vtl_alias '{new}' and the deprecated {deprecated} "
            f"'{old}' of the mapping {mapping.id} must have the same value.",
        )
    force_setattr(mapping, "vtl_alias", new or old)
    force_setattr(mapping, deprecated, new or old)


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

    @property
    def full_expression(self) -> str:
        """Return the full expression with the semicolon."""
        assign_operand = "<-" if self.is_persistent else ":="
        full_expression = f"{self.result} {assign_operand} {self.expression}"
        return (
            full_expression
            if full_expression.strip().endswith(";")
            else f"{full_expression};"
        )


class Ruleset(Item, frozen=True, omit_defaults=True):
    """A persistent set of rules, or a viral propagation.

    A ruleset can be invoked by the VTL operators. From VTL 2.2, it can
    also define a viral propagation, i.e. the algorithm for combining the
    values of a viral Attribute. A viral propagation is not invoked: it
    makes viral the Attributes it applies to, and it is applied by the
    operators that propagate them.

    Attributes:
        ruleset_definition: The VTL statement that defines the ruleset.
        ruleset_scope: The VTL artefact on which the ruleset is defined
            (a Variable or a Value Domain).
        ruleset_type: The VTL type of the ruleset (``viral`` for a viral
            propagation).
    """

    ruleset_definition: str = ""
    ruleset_scope: Optional[Literal["variable", "valuedomain"]] = None
    ruleset_type: Optional[Literal["datapoint", "hierarchical", "viral"]] = (
        None
    )


class UserDefinedOperator(Item, frozen=True, omit_defaults=True):
    """Custom VTL operator that extends the VTL standard library."""

    operator_definition: str = ""


class NamePersonalisation(Item, frozen=True, omit_defaults=True):
    """Definition of personalised name.

    Deprecated in SDMX 3.2: the names assigned by default by the VTL
    operators can be changed in the VTL program (e.g. with ``rename``).
    """

    personalised_name: str = ""
    vtl_artefact: str = ""
    vtl_default_name: str = ""


class VtlMapping(Item, frozen=True, omit_defaults=True):
    """Single mapping between a VTL alias and an SDMX artefact.

    The mappings are the definitions of the VTL Data Sets and Value
    Domains used by a VTL program: a VtlDatasetMapping maps a VTL Data Set
    and a VtlCodelistMapping a VTL Value Domain.

    Attributes:
        vtl_alias: The alias used in VTL for referencing the SDMX artefact,
            written without the single quotes that can enclose it in the
            VTL statements. It is unique within its VTL mapping scheme.
    """

    vtl_alias: str = ""

    @property
    def sdmx_urn(self) -> Optional[str]:
        """The URN of the SDMX artefact referenced through the alias."""
        return None


class ToVtlMapping(Struct, frozen=True, omit_defaults=True):
    """The mapping method and filter used when mapping from SDMX to VTL.

    Deprecated in SDMX 3.2: the Basic mapping is the only mapping method,
    and the parts of the data are selected in the VTL program or through
    the query parameters of a VtlExecution.
    """

    to_vtl_sub_space: Sequence[str] = ()
    method: Optional[str] = None


class FromVtlMapping(Struct, frozen=True, omit_defaults=True):
    """The mapping method and filter used when mapping from VTL to SDMX.

    Deprecated in SDMX 3.2: the Basic mapping is the only mapping method,
    and the parts of the data are combined in the VTL program.
    """

    from_vtl_sub_space: Sequence[str] = ()
    method: Optional[str] = None


class VtlDataflowMapping(
    VtlMapping, frozen=True, omit_defaults=True, kw_only=True
):
    """Single mapping with a dataflow.

    Deprecated in SDMX 3.2: replaced by the VtlDatasetMapping.

    Attributes:
        dataflow: The mapped dataflow.
        dataflow_alias: Deprecated in SDMX 3.2: replaced by the
            ``vtl_alias``. If both are set, they must have the same value.
        to_vtl_mapping_method: The mapping method from SDMX to VTL.
        from_vtl_mapping_method: The mapping method from VTL to SDMX.
    """

    dataflow: Union[Dataflow, DataflowRef]
    dataflow_alias: str = ""
    to_vtl_mapping_method: Optional[ToVtlMapping] = None
    from_vtl_mapping_method: Optional[FromVtlMapping] = None

    def __post_init__(self) -> None:
        """Aligns the aliases of the mapping.

        Raises:
            Invalid: If the mapping has no alias, or if the ``vtl_alias``
                and the ``dataflow_alias`` differ.
        """
        _sync_alias(self, "dataflow_alias")
        if not self.vtl_alias:
            raise Invalid(
                "Invalid VTL mapping",
                f"The mapping {self.id} must have a VTL alias.",
            )

    @property
    def sdmx_urn(self) -> Optional[str]:
        """The URN of the dataflow referenced through the alias."""
        return _urn(self.dataflow)


class VtlDatasetMapping(
    VtlMapping, frozen=True, omit_defaults=True, kw_only=True
):
    """Single mapping between a VTL Data Set and an SDMX artefact.

    The data structure of the VTL Data Set corresponds to the one of the
    mapped artefact through the Basic mapping.

    Attributes:
        sdmx_artefact: The Data Structure Definition, Dataflow or
            Provision Agreement the VTL Data Set is mapped to: the
            artefact, a reference to it or its URN.
        is_input: Whether the VTL Data Set is an input of the VTL program
            (True), whose definition and data are obtained from SDMX, or
            an output (False), whose data are converted into SDMX. An
            output must be the result of a persistent Transformation.
    """

    sdmx_artefact: Union[
        str,
        DataStructureDefinition,
        Dataflow,
        ProvisionAgreement,
        Reference,
    ]
    is_input: bool

    def __post_init__(self) -> None:
        """Checks the mapping.

        Raises:
            Invalid: If the VTL alias is missing, has white spaces or
                single quotes or is longer than 128 characters, or if the
                mapped artefact is not a Data Structure Definition,
                Dataflow or Provision Agreement.
        """
        if not _VTL_ALIAS.fullmatch(self.vtl_alias):
            raise Invalid(
                "Invalid VTL mapping",
                f"The VTL alias of the mapping {self.id} must have between "
                "1 and 128 characters, without white spaces or single "
                f"quotes, but it is '{self.vtl_alias}'.",
            )
        if not _is_maintainable(
            self.sdmx_artefact,
            "DataStructure",
            "Dataflow",
            "ProvisionAgreement",
        ):
            raise Invalid(
                "Invalid VTL mapping",
                f"The mapping {self.id} must reference a Data Structure "
                "Definition, Dataflow or Provision Agreement (the artefact, "
                "a reference to it or its URN).",
            )

    @property
    def sdmx_urn(self) -> Optional[str]:
        """The URN of the artefact referenced through the alias."""
        return _urn(self.sdmx_artefact)


class VtlCodelistMapping(VtlMapping, frozen=True, omit_defaults=True):
    """Single mapping between a VTL Value Domain and a codelist.

    Attributes:
        codelist: The mapped codelist, whose codes are the values of the
            Value Domain: the codelist, a reference to it or its URN.
        codelist_alias: Deprecated in SDMX 3.2: replaced by the
            ``vtl_alias``. If both are set, they must have the same value.
    """

    codelist: Union[str, Codelist, Reference] = ""
    codelist_alias: str = ""

    def __post_init__(self) -> None:
        """Aligns the aliases of the mapping.

        Raises:
            Invalid: If the ``vtl_alias`` and the ``codelist_alias``
                differ.
        """
        _sync_alias(self, "codelist_alias")

    @property
    def sdmx_urn(self) -> Optional[str]:
        """The URN of the codelist referenced through the alias."""
        return _urn(self.codelist)


class VtlConceptMapping(VtlMapping, frozen=True, omit_defaults=True):
    """Single mapping with a concept.

    Deprecated in SDMX 3.2: the VTL Variables correspond to the components
    having the same names in the VTL Data Sets and need no mapping.

    Attributes:
        concept: The mapped concept.
        concept_alias: Deprecated in SDMX 3.2: replaced by the
            ``vtl_alias``. If both are set, they must have the same value.
    """

    concept: Union[str, Concept, ItemReference] = ""
    concept_alias: str = ""

    def __post_init__(self) -> None:
        """Aligns the aliases of the mapping.

        Raises:
            Invalid: If the ``vtl_alias`` and the ``concept_alias`` differ.
        """
        _sync_alias(self, "concept_alias")

    @property
    def sdmx_urn(self) -> Optional[str]:
        """The URN of the concept referenced through the alias."""
        return _urn(self.concept)


class CustomType(Item, frozen=True, omit_defaults=True):
    """Custom specification for a VTL basic scalar type.

    Deprecated in SDMX 3.2: the default conversions between VTL and SDMX
    data types apply, and explicit conversions use the VTL ``cast``.
    """

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
    VTL_2_2 = "2.2"


class VtlScheme(ItemScheme, frozen=True, omit_defaults=True):
    """A VTL item scheme with the additional propery 'vtl_version'.

    Attributes:
        vtl_version: The version of the VTL used in the definitions of the
            scheme (e.g. ``2.2``). It is mandatory in the transformation,
            ruleset and user defined operator schemes of an SDMX message.
    """

    vtl_version: Optional[str] = None

    def __post_init__(self) -> None:
        """Additional validation checks for VTL item schemes.

        Version must be a valid VTL version.

        Raises:
            Invalid: If the version is not a valid VTL version
        """
        if (
            self.vtl_version is not None
            and self.vtl_version not in _VTLVersionEnum._value2member_map_
        ):
            raise Invalid(f"Invalid VTL version: {self.vtl_version}")


class CustomTypeScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of custom specifications for VTL basic scalar types.

    Deprecated in SDMX 3.2, like its items.
    """

    items: Sequence[CustomType] = ()


class NamePersonalisationScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of name personalisations.

    Deprecated in SDMX 3.2, like its items.
    """

    items: Sequence[NamePersonalisation] = ()


class VtlMappingScheme(ItemScheme, frozen=True, omit_defaults=True):
    """A collection of VTL mappings.

    The mappings define the VTL Data Sets and Value Domains used by a
    transformation scheme, also through its rulesets and user defined
    operators.
    """

    items: Sequence[VtlMapping] = ()

    def __post_init__(self) -> None:
        """Checks the scheme.

        Raises:
            Invalid: If the scheme has no agency, or if several mappings
                have the same VTL alias.
        """
        super().__post_init__()
        aliases = set()
        for mapping in self.items:
            alias = mapping.vtl_alias
            if alias and alias in aliases:
                raise Invalid(
                    "Invalid VTL mapping scheme",
                    f"The VTL alias '{alias}' must be unique within the "
                    f"VTL mapping scheme {self.id}.",
                )
            aliases.add(alias)


class RulesetScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of rulesets.

    Attributes:
        vtl_mapping_scheme: Deprecated in SDMX 3.2: the mappings used by
            the rulesets are in the VTL mapping scheme of the
            transformation scheme.
        items: The rulesets.
    """

    vtl_mapping_scheme: Optional[Union[str, VtlMappingScheme, Reference]] = (
        None
    )
    items: Sequence[Ruleset] = ()


class UserDefinedOperatorScheme(VtlScheme, frozen=True, omit_defaults=True):
    """A collection of user-defined operators.

    Attributes:
        vtl_mapping_scheme: Deprecated in SDMX 3.2: the mappings used by
            the operators are in the VTL mapping scheme of the
            transformation scheme.
        ruleset_schemes: Deprecated in SDMX 3.2: the rulesets used by the
            operators are in the ruleset schemes of the transformation
            scheme.
        items: The user-defined operators.
    """

    vtl_mapping_scheme: Optional[Union[str, VtlMappingScheme, Reference]] = (
        None
    )
    ruleset_schemes: Sequence[Union[str, RulesetScheme, Reference]] = ()
    items: Sequence[UserDefinedOperator] = ()


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
    a string (e.g. “2.2”), as the version of the VTL determines which syntax
    is used in defining the transformations of the scheme.
    This attribute is inherited from the VTLItemScheme class.

    The TransformationScheme references all the other schemes used by the
    VTL program: its ruleset and user-defined operator schemes contain all
    the rulesets and operators used by its transformations, also
    indirectly, and its VTL mapping scheme contains the mappings of the
    aliases used for referencing SDMX artefacts.

    Attributes:
        vtl_mapping_scheme: Optional[VtlMappingScheme].
          The VTL mapping scheme.
        name_personalisation_scheme: Optional[NamePersonalisationScheme].
          The name personalisation scheme (deprecated in SDMX 3.2).
        custom_type_scheme: Optional[CustomTypeScheme].
          The custom type scheme (deprecated in SDMX 3.2).
        ruleset_schemes: Sequence[RulesetScheme].
          The ruleset schemes.
        user_defined_operator_schemes: Sequence[UserDefinedOperatorScheme].
          The user-defined operator schemes.
    """

    vtl_mapping_scheme: Optional[Union[VtlMappingScheme, Reference]] = None
    name_personalisation_scheme: Optional[
        Union[NamePersonalisationScheme, Reference]
    ] = None
    custom_type_scheme: Optional[Union[CustomTypeScheme, Reference]] = None
    ruleset_schemes: Sequence[Union[RulesetScheme, Reference]] = ()
    user_defined_operator_schemes: Sequence[
        Union[UserDefinedOperatorScheme, Reference]
    ] = ()
    items: Sequence[Transformation] = ()


class QueryParameter(Struct, frozen=True, omit_defaults=True, kw_only=True):
    """A name-value pair used for retrieving the data of a VTL Data Set.

    Attributes:
        name: The name of the parameter (e.g. ``key``, ``startPeriod``),
            unique within its data extraction.
        value: The value of the parameter: mandatory if the parameter is
            fixed, otherwise a default value.
        is_fixed: Whether the value is fixed (True) or can be overridden
            at run time (False). A non-fixed parameter without value must
            be given a value at run time.
    """

    name: str
    value: Optional[str] = None
    is_fixed: bool

    def __post_init__(self) -> None:
        """Checks the parameter.

        Raises:
            Invalid: If the name is missing or has white spaces, or if the
                parameter is fixed and has no value.
        """
        if not _PARAMETER_NAME.fullmatch(self.name):
            raise Invalid(
                "Invalid query parameter",
                "The name of a query parameter must have at least one "
                f"character, without white spaces, but it is '{self.name}'.",
            )
        if self.is_fixed and self.value is None:
            raise Invalid(
                "Invalid query parameter",
                f"The parameter {self.name} has no value, but a fixed "
                "parameter must have a value.",
            )


class VtlDataExtraction(Struct, frozen=True, omit_defaults=True, kw_only=True):
    """How to retrieve the data of an input VTL Data Set.

    Its subclasses are the QueryExtraction and the UrlExtraction.

    Attributes:
        dataset_mapping: The VtlDatasetMapping of the input VTL Data Set,
            as a reference or as its URN. It belongs to the VTL mapping
            scheme of the transformation scheme to be executed.
        parameters: The query parameters used for retrieving the data.
    """

    dataset_mapping: Union[str, ItemReference]
    parameters: Sequence[QueryParameter] = ()

    def __post_init__(self) -> None:
        """Checks the data extraction.

        Raises:
            Invalid: If the data extraction does not reference a
                VtlDatasetMapping, or if several of its parameters have the
                same name.
        """
        short_urn = _short_urn(self.dataset_mapping) or ""
        if not (
            _ITEM.match(short_urn)
            and short_urn.startswith("VtlDatasetMapping=")
        ):
            raise Invalid(
                "Invalid data extraction",
                "A data extraction must reference a VtlDatasetMapping (a "
                f"reference or its URN), but got {self.dataset_mapping}.",
            )
        names = set()
        for parameter in self.parameters:
            if parameter.name in names:
                raise Invalid(
                    "Invalid data extraction",
                    f"The name of the query parameter '{parameter.name}' "
                    "must be unique within its data extraction.",
                )
            names.add(parameter.name)

    @property
    def dataset_mapping_urn(self) -> Optional[str]:
        """The URN of the VtlDatasetMapping of the input VTL Data Set."""
        return _urn(self.dataset_mapping)


class QueryExtraction(
    VtlDataExtraction, frozen=True, omit_defaults=True, kw_only=True
):
    """Retrieval of data from a web service compliant with the SDMX REST API.

    The VTL engine builds the data query for the context, if any, or
    otherwise for the SDMX artefact of the VtlDatasetMapping, according to
    the version of the SDMX REST API, by using the query parameters.

    Attributes:
        entry_point: The URL of the entry point of the web service.
        sdmx_api_version: The version of the SDMX REST API implemented by
            the entry point, as major.minor (e.g. ``2.1``). If not set,
            the default version of the web service is assumed.
        context: The Dataflow or Provision Agreement whose data are
            queried (the artefact, a reference to it or its URN), which
            uses the same Data Structure Definition as the SDMX artefact
            of the VtlDatasetMapping. If not set, the data of the latter
            are queried.
    """

    entry_point: str
    sdmx_api_version: Optional[str] = None
    context: Optional[Union[str, Dataflow, ProvisionAgreement, Reference]] = (
        None
    )

    def __post_init__(self) -> None:
        """Checks the query extraction.

        Raises:
            Invalid: If the entry point is missing, if the version of the
                SDMX REST API is not written as major.minor, if the context
                is not a Dataflow or Provision Agreement, or if the checks
                of any data extraction fail.
        """
        super().__post_init__()
        if not self.entry_point:
            raise Invalid(
                "Invalid data extraction",
                "A query extraction must have an entry point.",
            )
        if self.sdmx_api_version is not None and not (
            _SDMX_API_VERSION.fullmatch(self.sdmx_api_version)
        ):
            raise Invalid(
                "Invalid data extraction",
                "The version of the SDMX REST API must be written as "
                f"major.minor (e.g. 2.1), but it is {self.sdmx_api_version}.",
            )
        if self.context is not None and not _is_maintainable(
            self.context, "Dataflow", "ProvisionAgreement"
        ):
            raise Invalid(
                "Invalid data extraction",
                "The context of a query extraction must be a Dataflow or "
                "Provision Agreement (the artefact, a reference to it or "
                "its URN).",
            )

    @property
    def context_urn(self) -> Optional[str]:
        """The URN of the Dataflow or Provision Agreement to be queried."""
        return _urn(self.context)


class UrlExtraction(
    VtlDataExtraction, frozen=True, omit_defaults=True, kw_only=True
):
    """Retrieval of data through a URL built from a template.

    It is meant for web services that are not fully compliant with the
    SDMX REST API.

    Attributes:
        url_template: The complete URL of the query, whose tokens enclosed
            in curly braces (e.g. ``{startPeriod}``) are replaced by the
            values of the query parameters having the same names.
    """

    url_template: str

    def __post_init__(self) -> None:
        """Checks the URL extraction.

        Raises:
            Invalid: If the URL template is missing, or if the checks of
                any data extraction fail.
        """
        super().__post_init__()
        if not self.url_template:
            raise Invalid(
                "Invalid data extraction",
                "A URL extraction must have a URL template.",
            )


class VtlExecution(
    MaintainableArtefact, frozen=True, omit_defaults=True, kw_only=True
):
    """How to retrieve the data of the input VTL Data Sets of a VTL program.

    A VtlExecution is an execution configuration, maintained independently
    of the transformation scheme: several executions can reference the
    same transformation scheme, and an organisation can define executions
    for the transformation schemes of other organisations. The data of the
    inputs without a data extraction are provided at run time.

    Attributes:
        transformation_scheme: The transformation scheme to be executed:
            the scheme, a reference to it or its URN.
        extractions: The data extractions of the input VTL Data Sets, at
            most one for each input.
    """

    transformation_scheme: Union[str, TransformationScheme, Reference]
    extractions: Sequence[Union[QueryExtraction, UrlExtraction]] = ()

    def __post_init__(self) -> None:
        """Checks the execution.

        Raises:
            Invalid: If the execution has no agency, does not reference a
                transformation scheme, has no data extraction, or has
                several data extractions for the same VtlDatasetMapping.
        """
        super().__post_init__()
        if not _is_maintainable(
            self.transformation_scheme, "TransformationScheme"
        ):
            raise Invalid(
                "Invalid VTL execution",
                f"The VTL execution {self.id} must reference a "
                "Transformation Scheme (the scheme, a reference to it or "
                "its URN).",
            )
        if not self.extractions:
            raise Invalid(
                "Invalid VTL execution",
                f"The VTL execution {self.id} must have at least one data "
                "extraction.",
            )
        mappings = set()
        for extraction in self.extractions:
            mapping = _short_urn(extraction.dataset_mapping)
            if mapping in mappings:
                raise Invalid(
                    "Invalid VTL execution",
                    f"The VTL execution {self.id} must have at most one "
                    f"data extraction for {mapping}.",
                )
            mappings.add(mapping)

    @property
    def transformation_scheme_urn(self) -> Optional[str]:
        """The URN of the transformation scheme to be executed."""
        return _urn(self.transformation_scheme)
