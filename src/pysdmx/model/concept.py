"""Model for SDMX Concepts and Concept Schemes.

Concepts are used to **describe the relevant characteristics of statistical
domains**. For example, exchanges rates might be described with concepts such
as the numerator currency, the denominator currency, the type of exchange
rates, etc.

Additional information about the rules the values for a concept must follow
can be defined using ``DataType``, ``Facets`` or enumeration (i.e. list of
``codes``).
"""

from datetime import datetime
from enum import Enum
from typing import Iterator, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.model.__base import Item, ItemScheme
from pysdmx.model.code import Codelist


class DataType(str, Enum):
    """The expected data type for a concept."""

    ALPHA = "Alpha"
    """The alphabetic character set of A-Z, a-z.."""
    ALPHA_NUM = "AlphaNumeric"
    """The character set of A-Z, a-z and 0-9."""
    BASIC_TIME_PERIOD = "BasicTimePeriod"
    """The ISO standard periods."""
    BIG_INTEGER = "BigInteger"
    """Immutable arbitrary-precision signed integer."""
    BOOLEAN = "Boolean"
    """True or False."""
    COUNT = "Count"
    """A simple incrementing integer type."""
    DATE = "GregorianDay"
    """A ISO 8601 date (e.g. ``2011-06-17``)."""
    DATE_TIME = "DateTime"
    """An ISO 8601 point in time."""
    DAY = "Day"
    """A day in the ISO 8601 calendar (e.g. ``---31``)."""
    DECIMAL = "Decimal"
    """Immutable arbitrary-precision signed decimal number."""
    DOUBLE = "Double"
    """A decimal number (8 bytes)."""
    DURATION = "Duration"
    """An ISO 8601 duration."""
    FLOAT = "Float"
    """A decimal number (4 bytes)."""
    GREGORIAN_TIME_PERIOD = "GregorianTimePeriod"
    """This is the union of YEAR, YEAR_MONTH, and DATE."""
    INTEGER = "Integer"
    """A whole number (4 bytes)."""
    LONG = "Long"
    """A whole number (8 bytes)."""
    MONTH = "Month"
    """A month in the ISO 8601 calendar (e.g. ``12``)."""
    MONTH_DAY = "MonthDay"
    """A month day in the ISO 8601 calendar (e.g. ``--12-31``)."""
    NUMERIC = "Numeric"
    """The simple numeric character set of 0-9, treated as a string."""
    PERIOD = "ObservationalTimePeriod"
    """A reporting period. The format varies with the frequency."""
    REP_DAY = "ReportingDay"
    """The SDMX reporting period for daily frequency (e.g. 2025-D001)."""
    REP_MONTH = "ReportingMonth"
    """The SDMX reporting period for monthly frequency (e.g. 2025-M01)."""
    REP_QUARTER = "ReportingQuarter"
    """The SDMX reporting period for quarterly frequency (e.g. 2025-Q1)."""
    REP_SEMESTER = "ReportingSemester"
    """The SDMX reporting period for half-yearly frequency (e.g. 2025-S1)."""
    REP_TRIMESTER = "ReportingTrimester"
    """The SDMX reporting period for trimestrial frequency (e.g. 2025-T1)."""
    REP_WEEK = "ReportingWeek"
    """The SDMX reporting period for weekly frequency (e.g. 2025-W01)."""
    REP_YEAR = "ReportingYear"
    """The SDMX reporting period for yearly frequency (e.g. 2025-A1)."""
    SHORT = "Short"
    """A whole number (2 bytes)."""
    STD_TIME_PERIOD = "StandardTimePeriod"
    """The ISO standard periods and the SDMX reporting periods."""
    STRING = "String"
    """A string (as immutable sequence of Unicode code points)."""
    TIME = "Time"
    """An ISO 8601 time (e.g. ``12:50:42``)."""
    URI = "URI"
    """A uniform resource identifier, such as a URL."""
    XHTML = "XHTML"
    """XHTML (or HTML) markup."""
    YEAR = "GregorianYear"
    """An ISO 8601 year (e.g. ``2000``)."""
    YEAR_MONTH = "GregorianYearMonth"
    """An ISO 8601 year and month (e.g. ``2000-01``)."""

    def __str__(self) -> str:
        """Data Type String representation."""
        return self.value

    def __repr__(self) -> str:
        """Data Type String representation."""
        return f"{self.__class__.__name__}.{self._name_}"


class Facets(Struct, frozen=True, omit_defaults=True, repr_omit_defaults=True):
    """Additional information about the concept expected values.

    The facets that apply vary with the type. For example,
    ``min_mength`` and ``max_length`` are typically used with
    strings, while ``start_value`` and ``end_value`` are typically
    used with numeric sequences.
    """

    min_length: Optional[int] = None
    """The minimum length for the value (e.g. ``1`` character)."""
    max_length: Optional[int] = None
    """The maximum length for the value (e.g. ``256`` characters)."""
    min_value: Optional[Union[int, float]] = None
    """Used by ranges to indicate what the lower bound of the range is."""
    max_value: Optional[Union[int, float]] = None
    """Used by ranges to indicate what the upper bound of the range is."""
    start_value: Optional[Union[int, float]] = None
    """Used in a numeric sequence to indicate its starting point."""
    end_value: Optional[Union[int, float]] = None
    """Used in a numeric sequence to indicate its ending point."""
    interval: Optional[Union[int, float]] = None
    """The permitted interval (increment) in a sequence."""
    time_interval: Optional[str] = None
    """The permitted duration in a time sequence."""
    decimals: Optional[int] = None
    """The number of characters allowed after the decimal separator."""
    pattern: Optional[str] = None
    """A regular expression the value must match."""
    start_time: Optional[datetime] = None
    """Indicates the starting point of a sequence."""
    end_time: Optional[datetime] = None
    """Indicates the ending point of a sequence."""
    is_sequence: bool = False
    """Whether the values are intended to be ordered."""
    is_multilingual: bool = False
    """Whether the text can be in multiple languages."""

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class Concept(Item, frozen=True, omit_defaults=True, tag=True):
    """A concept (aka **variable**), such as frequency, reference area, etc.

    Concepts are used to **describe the relevant characteristics** of a
    statistical domain. For example, exchanges rates might be described with
    concepts such as the numerator currency, the denominator currency,
    the type of exchange rates, etc.

    Some of these concepts are expected to be useful **across statistical
    domains**. Examples of such concepts include the frequency, the
    observation status, the confidentiality, etc.

    The *codes* field indicates the expected (i.e. allowed) set of values a
    concept can take within a particular domain. In addition to
    (or instead of) a set of codes, additional details about the expected
    format may be found in the *facets* and *dtype* fields.


    Attributes:
        id: A unique identifier for the concept (e.g. FREQ).
        dtype: The concept's data type (string, number, etc.).
        facets: Additional details such as the concept's minimum length.
        name: The concept's name.
        description: Additional descriptive information about the concept.
        codes: The expected values for the concept (e.g. a list of currency
            codes).
        enum_ref: The URN of the enumeration (codelist or valuelist) from
            which the codes are taken.
    """

    dtype: Optional[DataType] = None
    facets: Optional[Facets] = None
    codes: Optional[Codelist] = None
    enum_ref: Optional[str] = None


class ConceptScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of concepts.

    A concept scheme is **maintained by its agency**, typically, an
    organisation like the BIS, the ECB, the IMF, SDMX, etc.

    A concept scheme has an **identifier** and a **name**. It may also have a
    **description** and a **version**.

    A concept scheme is **iterable**, i.e. it can be used directly in a for
    loop.

    Attributes:
        id: The identifier for the scheme (e.g. CROSS_DOMAIN_CONCEPTS).
        name: The scheme name (e.g. "SDMX Cross Domain Concepts").
        agency: The maintainer of the scheme (e.g. SDMX).
        description: Additional descriptive information about the scheme
            (e.g. "The set of concepts in the SDMX Glossary").
        version: The scheme version (e.g. 2.0)
    """

    items: Sequence[Concept] = ()

    @property
    def concepts(self) -> Sequence[Concept]:
        """Extract the items in the Concept Scheme."""
        return self.items

    def __iter__(self) -> Iterator[Concept]:
        """Return an iterator over the list of concepts."""
        yield from self.concepts

    def __len__(self) -> int:
        """Return the number of concepts in the concept scheme."""
        return len(self.concepts)

    def __getitem__(self, id_: str) -> Optional[Concept]:
        """Return the concept identified by the given ID."""
        out = list(filter(lambda concept: concept.id == id_, self.concepts))
        if len(out) == 0:
            return None
        else:
            return out[0]

    def __contains__(self, id_: str) -> bool:
        """Whether a concept with the supplied ID is present in the scheme."""
        return bool(self.__getitem__(id_))
