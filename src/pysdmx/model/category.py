"""Model for SDMX Categories.

An example of a category scheme is one which categorises data, sometimes
known as a subject matter domain scheme or a data category scheme.
"""

from typing import Iterator, List, Optional, Sequence, Set

from pysdmx.model.__base import DataflowRef, Item, ItemScheme


class Category(Item, frozen=False, omit_defaults=True):  # type: ignore[misc]
    """A category, ie a way to **organize and group** things.

    Categories are used to organize and group other artefacts in SDMX.
    A typical example would be to organize dataflows by topics
    (e.g. derivatives, exchange rates, etc.)

    Categories can be **nested**, up to any level of depth and,
    therefore, a category is **iterable**.

    Attributes:
        id: The category ID (e.g. TOPIC_001)
        name: The category name (e.g. "Locational banking statistics")
        description: Additionale descriptive information about the
            category (e.g. "These statistics cover the balance sheets
            of internationally active banks.")
        categories: The sub-categories, i.e. the categories belonging
            to the category.
        dataflows: The list of dataflows attached to the category.
    """

    categories: Sequence["Category"] = ()
    dataflows: Sequence[DataflowRef] = ()

    def __iter__(self) -> Iterator["Category"]:
        """Return an iterator over the list of categories."""
        yield from self.categories


class CategoryScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of categories, likes a list of topics.

    A category scheme is **maintained by its agency**, typically, an
    organisation like the BIS, the ECB, the IMF, SDMX, etc.

    A category scheme has an **identifier** and a **name**. It may also
    have a **description** and **version**.

    A category scheme is **iterable**.

    While every category contains the list of dataflows attached to it,
    the ``dataflows`` property of the ``CategoryScheme`` can be used
    to retrieve (as a set) the list of dataflows attached to any of the
    categories in the scheme.

    Attributes:
        id: The identifier for the scheme (e.g. STAT_SUBJECT_MATTER).
        name: The scheme name (e.g. "SDMX Statistical Subject-Matter
            Domains").
        agency: The maintainer of the scheme (e.g. SDMX).
        description: Additional descriptive information about the scheme
            (e.g. "The SDMX Content Guidelines for Statistical
            Subject-Matter Domains").
        version: The scheme version (e.g. 1.0)
    """

    @property
    def categories(self) -> Sequence[Category]:
        """The list of top level categories in the scheme."""
        return self.items  # type: ignore[return-value]

    @property
    def dataflows(self) -> Sequence[DataflowRef]:
        """Return the dataflows attached to any category in the scheme."""
        flows: Set[DataflowRef] = set()
        for cat in self.categories:
            flows.update(self.__extract_flows(cat))
        return list(flows)

    def __iter__(self) -> Iterator[Category]:
        """Return an iterator over the list of categories."""
        yield from self.categories

    def __len__(self) -> int:
        """Return the number of categories in the category scheme."""
        return self.__get_count(self.categories)

    def __getitem__(self, id_: str) -> Optional[Category]:
        """Return the category identified by the given ID."""
        return self.__extract_cat(self.categories, id_)

    def __contains__(self, id_: str) -> bool:
        """Whether there is a category with the supplied ID in the scheme."""
        return bool(self.__getitem__(id_))

    def __get_count(self, categories: Sequence[Category]) -> int:
        """Return the number of categories at all levels."""
        count = len(categories)
        for cat in categories:
            if cat.categories:
                count += self.__get_count(cat.categories)
        return count

    def __extract_cat(
        self, categories: Sequence[Category], id_: str
    ) -> Optional[Category]:
        if "." in id_:
            ids = id_.split(".")
            out = list(filter(lambda cat: cat.id == ids[0], categories))
            if out:
                pkey = ".".join(ids[1:])
                return self.__extract_cat(out[0].categories, pkey)
        else:
            out = list(filter(lambda cat: cat.id == id_, categories))
            if out:
                return out[0]
        return None

    def __extract_flows(self, c: Category) -> Sequence[DataflowRef]:
        flows: List[DataflowRef] = []
        if c.dataflows:
            flows.extend(c.dataflows)
        for sub in c.categories:
            flows.extend(self.__extract_flows(sub))
        return flows
