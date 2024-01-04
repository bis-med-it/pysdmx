"""Model for Mapping Definitions."""

from datetime import datetime
from re import Pattern
from typing import Any, Literal, Optional, Sequence, Union

from msgspec import Struct


class FixedDatePatternMap(Struct, frozen=True, omit_defaults=True):
    """A mapping based on a date pattern.

    Examples:
        For example, let's assume a component in the source, with ID `DATE`,
        and containing string values such as `Sep 23`. In the target, we want
        this to be mapped to the `TIME_PERIOD` component, with ISO 8601
        periods for monthly data (e.g. `2023-09`). This can be expressed with
        the following mapping:

            >>> FixedDatePatternMap("DATE", "TIME_PERIOD", "MMM yy", "M")


    Attributes:
        source: The ID of the source component.
        target: The ID of the target component.
        pattern: Describes the source date using conventions for describing
            years, months, days, etc
        frequency: The frequency to convert the input date into or a
            reference to a dimension or an atttribute with the frequency code.
            See `pattern_type` below for additional information.
        id: The Map ID, as defined in the Registry.
        locale: The locale on which the input will be parsed according to the
            pattern.
        pattern_type: The type of date pattern, i.e. fixed or variable. When
            the type is `fixed`, `frequency` is a fixed value from the
            frequency codelist (e.g. `A` for annual frequency). When the type
            is `variable`, `frequency` references a dimension or attribute in
            the target structure (e.g. `FREQ`). In this case, the input date
            can be converted to a different format, depending on the
            frequency of the converted data.
    """

    source: str
    target: str
    pattern: str
    frequency: str
    id: Optional[str] = None
    locale: str = "en"
    pattern_type: Literal["fixed", "variable"] = "fixed"


class ValueSetter(Struct, frozen=True, omit_defaults=True):
    """A mapping setting a fixed or default value in the target.

    Examples:
        For example, let's assume that all observations in the target must be
        treated as free for publication. This can be expressed with the
        following mapping:

            >>> ValueSetter("CONF_STATUS", "F")

    Attributes:
        target:
            The ID of the component for which we want to set the fixed value.
        value: The fixed value to be set in the referenced component.
        is_fixed:
            Whether the value must be set regardless of whether a value is
            already set for the component.
    """

    target: str
    value: Any
    is_fixed: bool = True


class ImplicitMapper(Struct, frozen=True, omit_defaults=True):
    """A mapping where the value in the source is copied to the target.

    Examples:
        For example, let's assume a component in the source (`OBS_CONF`),
        indicating the confidentiality of data, that we want to map as-is to
        a target component (`CONF_STATUS`). This can be expressed with the
        following mapping:

        >>> ImplicitMapper("OBS_CONF", "CONF_STATUS")

    Attributes:
        source:
            The ID of the source component to be mapped, from which
            we want to copy the value.
        target: The ID of the target component.
    """

    source: str
    target: str


class MultipleValueMap(Struct, frozen=True, omit_defaults=True):
    """Provides the values for a mapping between one or more components.

    Examples:
        For example, let's assume that we want to map the the code for local
        currency (say `LC`) to an ISO 3-letter currency code, depending on the
        country. So, if the country is `DE` (Germany), then the currency in
        the target should be `EUR` but, if the country is `CH`, then it should
        be `CHF`. This can be expressed with the following value maps:

        >>> MultipleValueMap(["DE", "LC"], ["EUR"])
        >>> MultipleValueMap(["CH", "LC"], ["CHF"])

    Also, the mapping can depending on the time period.

    Examples:
        For example, for periods before January 1999, we may want to map the
        local currency for Germany to `DEM` and afterwards to `EUR`. This can
        be expressed with the following value maps:

        >>> from datetime import datetime
        >>> t1 = datetime(1998, 12, 31, 23, 59, 59)
        >>> t2 = datetime(1999, 1, 1)
        >>> MultipleValueMap(["DE", "LC"], ["EUR"], valid_to: t1)
        >>> MultipleValueMap(["DE", "LC"], ["EUR"], valid_from: t2)
        >>> MultipleValueMap(["CH", "LC"], ["CHF"])

    Values in the source may represent regular expressions with capture
    groups.

    Attributes:
        source: One or more source values
        target: One or more target values
        valid_from: Start of business validity for the mapping
        valid_to: End of business validity for the mapping
    """

    source: Sequence[Union[str, Pattern[str]]]
    target: Sequence[str]
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class ValueMap(Struct, frozen=True, omit_defaults=True):
    """Maps the values of two components together.

    Examples:
        For example, let's assume that we want to map the ISO 2-letter country
        code with the ISO 3-letter country code. This can be expressed with
        the following value maps:

            >>> ValueMap("BE", "BEL")

    Values in the source may represent regular expressions with capture
    groups.

    Also, a map may have business validity associated with it.

    Attributes:
        source: The source value
        target: The target value
        valid_from: Start of business validity for the mapping
        valid_to: End of business validity for the mapping
    """

    source: Union[str, Pattern[str]]
    target: str
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class MultipleComponentMapper(Struct, frozen=True, omit_defaults=True):
    """Maps one or more source components to one or more target components.

    Examples:
        For example, let's assume that we want to map the the code for local
        currency (say `LC`) to an ISO 3-letter currency code, depending on the
        country. So, if the country is `DE` (Germany), then the currency in
        the target should be `EUR` but, if the country is `CH`, then it should
        be `CHF`. This can be expressed as follows:

            >>> de = MultipleValueMap(["DE", "LC"], ["EUR"])
            >>> ch = MultipleValueMap(["CH", "LC"], ["CHF"])
            >>> src = ["COUNTRY", "CURRENCY"]
            >>> tgt = ["CURRENCY"]
            >>> cm = MultipleComponentMapper(src, tgt, [de, ch])

    Attributes:
        source: The source component(s)
        target: The target component(s)
        values: The list of mapped values (one or more in the source and one
            or more in the target)
    """

    source: Sequence[str]
    target: Sequence[str]
    values: Sequence[MultipleValueMap]


class ComponentMapper(Struct, frozen=True, omit_defaults=True):
    """Maps a source component to a target component.

    Examples:
        For example, let's assume that we want to map the country code from
        an ISO 2-letter country code to an ISO 3-letter country code. This
        can be expressed as follows:

        >>> ar = ValueMap("AR", "ARG")
        >>> uy = ValueMap("UY", "URY")
        >>> cm = ComponentMapper("COUNTRY", "COUNTRY", [ar, uy])

    Attributes:
        source: The source component
        target: The target component
        values: The list of mapped values (one in the source and
            one in the target)
    """

    source: str
    target: str
    values: Sequence[ValueMap]


class MappingDefinition(Struct, frozen=True, omit_defaults=True):
    """Maps a source structure to a target structure.

    The various mapping rules are classified by types.

    Attributes:
        component_maps: The list of mappings between one source component
            and one target component.
        date_maps: The list of mappings based on date patterns
        fixed_value_maps: The list of mappings with a fixed value
        implicit_maps: The list of mappings where the value in the source
            is copied to the target.
        multiple_component_maps: The list of mappings between one or more
            source components and one or more target components.
    """

    component_maps: Sequence[ComponentMapper] = ()
    date_maps: Sequence[FixedDatePatternMap] = ()
    fixed_value_maps: Sequence[ValueSetter] = ()
    implicit_maps: Sequence[ImplicitMapper] = ()
    multiple_component_maps: Sequence[MultipleComponentMapper] = ()
