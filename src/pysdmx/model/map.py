"""Model for Mapping Definitions."""

from datetime import datetime
from re import Pattern
from typing import Any, Iterator, Literal, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.model.__base import MaintainableArtefact
from pysdmx.model.concept import DataType
from pysdmx.util import convert_dpm


class DatePatternMap(Struct, frozen=True, omit_defaults=True):
    """A mapping based on a date pattern.

    Examples:
        For example, let's assume a component in the source, with ID `DATE`,
        and containing string values such as `Sep 23`. In the target, we want
        this to be mapped to the `TIME_PERIOD` component, with ISO 8601
        periods for monthly data (e.g. `2023-09`). This can be expressed with
        the following mapping:

            >>> DatePatternMap("DATE", "TIME_PERIOD", "MMM yy", "M")


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

    @property
    def py_pattern(self) -> str:
        """Translate SDMX pattern into Python format codes."""
        return convert_dpm(self.pattern)


class FixedValueMap(Struct, frozen=True, omit_defaults=True):
    """Set a component to a fixed value.

    Examples:
        For example, let's assume that all observations in the target must be
        treated as free for publication. This can be expressed with the
        following mapping:

            >>> FixedValueMap("CONF_STATUS", "F")

    Attributes:
        target: The ID of the component to which the fixed value is assigned.
        value: The fixed value of the referenced component.
        located_in: Whether the component with a fixed value is in the source
            structure or the target structure. It usually is in the target
            structure (the default), but it can also be in the source, in case
            of bi-directional mapping.
    """

    target: str
    value: Any
    located_in: Literal["source", "target"] = "target"


class ImplicitComponentMap(Struct, frozen=True, omit_defaults=True):
    """A mapping where the value in the source is copied to the target.

    Examples:
        For example, let's assume a component in the source (`OBS_CONF`),
        indicating the confidentiality of data, that we want to map as-is to
        a target component (`CONF_STATUS`). This can be expressed with the
        following mapping:

        >>> ImplicitComponentMap("OBS_CONF", "CONF_STATUS")

    Attributes:
        source:
            The ID of the source component to be mapped, from which
            we want to copy the value.
        target: The ID of the target component.
    """

    source: str
    target: str


class MultiValueMap(Struct, frozen=True, omit_defaults=True):
    """Provides the values for a mapping between one or more components.

    Examples:
        For example, let's assume that we want to map the the code for local
        currency (say `LC`) to an ISO 3-letter currency code, depending on the
        country. So, if the country is `DE` (Germany), then the currency in
        the target should be `EUR` but, if the country is `CH`, then it should
        be `CHF`. This can be expressed with the following value maps:

        >>> MultiValueMap(["DE", "LC"], ["EUR"])
        >>> MultiValueMap(["CH", "LC"], ["CHF"])

    Also, the mapping can depending on the time period.

    Examples:
        For example, for periods before January 1999, we may want to map the
        local currency for Germany to `DEM` and afterwards to `EUR`. This can
        be expressed with the following value maps:

        >>> from datetime import datetime
        >>> t1 = datetime(1998, 12, 31, 23, 59, 59)
        >>> t2 = datetime(1999, 1, 1)
        >>> MultiValueMap(["DE", "LC"], ["EUR"], valid_to: t1)
        >>> MultiValueMap(["DE", "LC"], ["EUR"], valid_from: t2)
        >>> MultiValueMap(["CH", "LC"], ["CHF"])

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


class MultiRepresentationMap(
    MaintainableArtefact, frozen=True, omit_defaults=True
):
    """Maps one or more source codelists to one or more target codelists.

    A representation map is iterable, i.e. it is possible to iterate over
    the various mappings using a `for` loop.

    Attributes:
        id: The identifier for the representation map.
        name: The representation map's name.
        agency: The maintainer of the representation map.
        source: The URN(s) of the source codelist(s) / valuelist(s),
            or data type(s).
        target: The URN(s) of the target codelist(s) / valuelist(s),
            or data type(s).
        maps: The various mappings in the representation map.
        description: Additional descriptive information about the
            representation map.
        version: The version of the representation map.
    """

    source: Sequence[Union[str, DataType]] = []
    target: Sequence[Union[str, DataType]] = []
    maps: Sequence[MultiValueMap] = []

    def __iter__(
        self,
    ) -> Iterator[MultiValueMap]:
        """Return an iterator over the different maps."""
        yield from self.maps

    def __len__(self) -> int:
        """Return the number of maps in the representation map."""
        return len(self.maps)


class MultiComponentMap(Struct, frozen=True, omit_defaults=True):
    """Maps one or more source components to one or more target components.

    Examples:
        For example, let's assume that we want to map the the code for local
        currency (say `LC`) to an ISO 3-letter currency code, depending on the
        country. So, if the country is `DE` (Germany), then the currency in
        the target should be `EUR` but, if the country is `CH`, then it should
        be `CHF`. This can be expressed as follows:

            >>> de = MultiValueMap(["DE", "LC"], ["EUR"])
            >>> ch = MultiValueMap(["CH", "LC"], ["CHF"])
            >>> src = ["COUNTRY", "CURRENCY"]
            >>> tgt = ["CURRENCY"]
            >>> cm = MultiComponentMap(src, tgt, [de, ch])

    Attributes:
        source: The source component(s)
        target: The target component(s)
        values: The representation map, with the list of mapped values
            (one or more in the source and one or more in the target)
    """

    source: Sequence[str]
    target: Sequence[str]
    values: MultiRepresentationMap


class RepresentationMap(MaintainableArtefact, frozen=True, omit_defaults=True):
    """Maps one source codelist to a target codelist.

    A representation map is iterable, i.e. it is possible to iterate over
    the various mappings using a `for` loop.

    Attributes:
        id: The identifier for the representation map.
        name: The representation map's name.
        agency: The maintainer of the representation map.
        source: The URN of the source codelist / valuelist or a data type.
        target: The URN of the target codelist / valuelist or a data type.
        maps: The various mappings in the representation map.
        description: Additional descriptive information about the
            representation map.
        version: The version of the representation map.
    """

    source: Union[str, DataType, None] = None
    target: Union[str, DataType, None] = None
    maps: Sequence[ValueMap] = []

    def __iter__(
        self,
    ) -> Iterator[ValueMap]:
        """Return an iterator over the different maps."""
        yield from self.maps

    def __len__(self) -> int:
        """Return the number of maps in the representation map."""
        return len(self.maps)


class ComponentMap(Struct, frozen=True, omit_defaults=True):
    """Maps a source component to a target component.

    Examples:
        For example, let's assume that we want to map the country code from
        an ISO 2-letter country code to an ISO 3-letter country code. This
        can be expressed as follows:

        >>> ar = ValueMap("AR", "ARG")
        >>> uy = ValueMap("UY", "URY")
        >>> cm = ComponentMap("COUNTRY", "COUNTRY", [ar, uy])

    Attributes:
        source: The source component
        target: The target component
        values: The representation map, with the list of mapped values
            (one in the source and one in the target)
    """

    source: str
    target: str
    values: RepresentationMap


class StructureMap(MaintainableArtefact, frozen=True, omit_defaults=True):
    """Maps a source structure to a target structure.

    The various mapping rules are classified by types.

    A structure map is an iterable, i.e. it is possible to iterate over
    the various mapping rules using a `for` loop.

    It is also possible to retrieve the mapping rule applying to a component
    by using the component id (e.g. `map["FREQ"]`).

    Attributes:
        id: The identifier for the structure map.
        name: The name of the structure map.
        agency: The maintainer of the structure map.
        source: The source structure.
        target: The target structure.
        maps: The various mapping rules in the structure map.
        description: Additional descriptive information about the structure
            map.
        version: The version of the structure map (e.g. 2.0.42).
    """

    source: str = ""
    target: str = ""
    maps: Sequence[
        Union[
            ComponentMap,
            DatePatternMap,
            FixedValueMap,
            ImplicitComponentMap,
            MultiComponentMap,
        ]
    ] = []

    @property
    def component_maps(self) -> Sequence[ComponentMap]:
        """Maps between one source and one target component."""
        return list(
            filter(
                lambda i: isinstance(  # type: ignore[arg-type]
                    i,
                    ComponentMap,
                ),
                self.maps,
            )
        )

    @property
    def date_pattern_maps(self) -> Sequence[DatePatternMap]:
        """Maps based on date patterns."""
        return list(
            filter(
                lambda i: isinstance(  # type: ignore[arg-type]
                    i,
                    DatePatternMap,
                ),
                self.maps,
            )
        )

    @property
    def fixed_value_maps(self) -> Sequence[FixedValueMap]:
        """Maps with a fixed value."""
        return list(
            filter(
                lambda i: isinstance(  # type: ignore[arg-type]
                    i,
                    FixedValueMap,
                ),
                self.maps,
            )
        )

    @property
    def implicit_component_maps(self) -> Sequence[ImplicitComponentMap]:
        """Maps where the source value is copied to the target."""
        return list(
            filter(
                lambda i: isinstance(  # type: ignore[arg-type]
                    i,
                    ImplicitComponentMap,
                ),
                self.maps,
            )
        )

    @property
    def multi_component_maps(self) -> Sequence[MultiComponentMap]:
        """Maps between one or more source & one or more target components."""
        return list(
            filter(
                lambda i: isinstance(  # type: ignore[arg-type]
                    i,
                    MultiComponentMap,
                ),
                self.maps,
            )
        )

    def __iter__(
        self,
    ) -> Iterator[
        Union[
            ComponentMap,
            DatePatternMap,
            FixedValueMap,
            ImplicitComponentMap,
            MultiComponentMap,
        ]
    ]:
        """Return an iterator over the different mapping rules."""
        yield from self.maps

    def __len__(self) -> int:
        """Return the number of mapping rules in the structure map."""
        return len(self.maps)

    def __getitem__(self, id_: str) -> Optional[
        Sequence[
            Union[
                ComponentMap,
                DatePatternMap,
                FixedValueMap,
                ImplicitComponentMap,
                MultiComponentMap,
            ]
        ]
    ]:
        """Return the mapping rules for the supplied component."""
        out = []
        for m in self.maps:
            if (
                hasattr(m, "source") and (m.source == id_ or id_ in m.source)
            ) or (isinstance(m, FixedValueMap) and m.target == id_):
                out.append(m)
        if len(out) == 0:
            return None
        else:
            return out
