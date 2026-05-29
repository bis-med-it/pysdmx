"""Model for SDMX Concepts and Concept Schemes.

Concepts are used to **describe the relevant characteristics of statistical
domains**. For example, exchanges rates might be described with concepts such
as the numerator currency, the denominator currency, the type of exchange
rates, etc.

Additional information about the rules the values for a concept must follow
can be defined using ``DataType``, ``Facets`` or enumeration (i.e. list of
``codes``).
"""

from typing import Iterator, Optional, Sequence

from pysdmx.model.__base import DataType, Facets, Item, ItemScheme
from pysdmx.model.code import Codelist


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
