"""Model for SDMX Codes and Codelists.

Two different types of collections are provided:

- Codelist: A flat structure, i.e. a structure where all codes are at the same
  level. In SDMX terms, this structure can be fed from information stored
  as a *codelist* or a *value list*.
- Hierarchy: A structure where codes can be organized in a hierarchical
  fashion, like a list of country groups and their respective countries.

This is an example of what is meant with pysdmx being opinionated.
While SDMX allows two different types of hierarchies (simple hierarchies
expressed as codelists, and more complex hierarchies expressed as SDMX
hierarchies), pysdmx expects codelists and value lists to be flat (which
seems to be the vast majority of the cases), thereby leaving the
representation of hierarchical relationships to hierarchies only.
"""

from datetime import datetime
from typing import Iterator, Literal, Optional, Sequence

from msgspec import Struct

from pysdmx.model.__base import Item, ItemScheme, MaintainableArtefact


class Code(Item, frozen=True, omit_defaults=True):
    """A code, such as a country code in the list of ISO 3166 codes.

    Codes may have business validity information.

    Attributes:
        id: The identifier for the code (e.g. UY).
        name: The code's name (e.g. Uruguay).
        description: Additional descriptive information about the code.
        valid_from: Start of the code's validity period.
        valid_to: End of the code's validity period.
    """

    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class Codelist(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of codes, such as the ISO 3166 country codes.

    A codelist is **maintained by its agency**, typically, an organisation
    like the BIS, the ECB, the IMF, etc.

    A codelist has an **identifier** and a **name**. It may also have a
    **description** and **business validity information**.

    A codelist is **iterable**, i.e. it can be used as is in a for loop.

    A codelist represents a flat list of codes, without any hierarchical
    relationship between them. Both SDMX codelists and SDMX value lists
    are represented as a Codelist class.

    Attributes:
        id: The identifier for the codelist (e.g. CL_FREQ).
        name: The codelist name (e.g. "Frequency codelist").
        agency: The maintainer of the codelist (e.g. SDMX).
        description: Additional descriptive information about the codelist
            (e.g. "This codelist provides a set of values indicating the
            frequency of the data").
        version: The codelist version (e.g. 2.0.42)
    """

    sdmx_type: Literal["codelist", "valuelist"] = "codelist"

    @property
    def codes(self) -> Sequence[Code]:
        """Extract the items in the Codelist."""
        return self.items  # type: ignore[return-value]

    def __iter__(self) -> Iterator[Code]:
        """Return an iterator over the list of codes."""
        yield from self.codes

    def __len__(self) -> int:
        """Return the number of codes in the codelist."""
        return len(self.codes)

    def __getitem__(self, id_: str) -> Optional[Code]:
        """Return the code identified by the supplied ID."""
        out = list(filter(lambda code: code.id == id_, self.codes))
        if len(out) == 0:
            return None
        else:
            return out[0]

    def __contains__(self, id_: str) -> bool:
        """Whether a code with the supplied ID is present in the codelist."""
        return bool(self.__getitem__(id_))


class HierarchicalCode(Struct, frozen=True, omit_defaults=True):
    """A code, as used in a hierarchy.

    Hierachical codes may contain other codes.

    As codes, hierarchial codes may have business validity information.
    In addition, they may also have business validity associated with
    their relationship in the hierarchy.

    For example, let's imagine a hierarchy representing country groups.
    A country might have a valid_from property, with the date that
    country declared its independence. In addition, it may also
    have a rel_valid_from property, with the date the country joined
    that particular group (e.g. European Union).

    Attributes:
        id: The identifier for the code (e.g. UY).
        name: The code's name (e.g. Uruguay).
        description: Additional descriptive information about the code.
        valid_from: Start of the code's validity period.
        valid_to: End of the code's validity period.
        rel_valid_from: Start of the hierarchical relationship validity.
        rel_valid_to: End of the hierarchical relationship validity.
        codes: The child codes.
    """

    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None
    rel_valid_from: Optional[datetime] = None
    rel_valid_to: Optional[datetime] = None
    codes: Sequence["HierarchicalCode"] = ()

    def __iter__(self) -> Iterator["HierarchicalCode"]:
        """Return an iterator over the list of codes."""
        yield from self.codes

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        out = self.id
        if self.name:
            out = f"{out} ({self.name})"
        return out


class Hierarchy(MaintainableArtefact, frozen=True, omit_defaults=True):
    """An immutable collection of codes, organized hierarchically.

    A hierarchy is **maintained by its agency**, typically, an organisation
    like the BIS, the ECB, the IMF, etc.

    A hierarchy has an **identifier** and a **name**. It may also have a
    **description** and **business validity information**.

    A hierarchy is **iterable**, i.e. it can be used as is in a for loop.

    Attributes:
        id: The identifier for the hierarchy (e.g. AREA).
        name: The hierarchy name (e.g. "Country groups and their composition").
        agency: The maintainer of the hierarchy (e.g. SDMX).
        description: Additional descriptive information about the hierarchy
            (e.g. "This hierarchy provides a set of country groups and their
            respective composition").
        version: The hierarchy version (e.g. 2.0.42)
        codes: The list of codes in the hierarchy.
        operator: The URN of the operator to be applied to the items of an
            hierarchy. This is mainly used for data validation or data
            compilation purposes. For example, Let's assume a hierarchy with
            a top level code (A), with 2 child codes (B and C). And let's
            assume that the operator property references a VTL operator
            representing a sum. This can then be used for validation purposes,
            to check that A = B + C.
    """

    codes: Sequence[HierarchicalCode] = ()
    operator: Optional[str] = None

    def __iter__(self) -> Iterator[HierarchicalCode]:
        """Return an iterator over the list of codes."""
        yield from self.codes

    def __len__(self) -> int:
        """Return the number of codes in the hierarchy."""
        return self.__get_count(self.codes)

    def __getitem__(self, id_: str) -> Optional[HierarchicalCode]:
        """Return the code identified by the supplied ID."""
        return self.__extract_code(self.codes, id_)

    def __contains__(self, id_: str) -> bool:
        """Whether a code with the supplied ID is present in the hierarchy."""
        return bool(self.__getitem__(id_))

    def __get_count(self, codes: Sequence[HierarchicalCode]) -> int:
        """Return the number of codes at all levels."""
        count = len(codes)
        for code in codes:
            if code.codes:
                count += self.__get_count(code.codes)
        return count

    def __extract_code(
        self, codes: Sequence[HierarchicalCode], id_: str
    ) -> Optional[HierarchicalCode]:
        if "." in id_:
            ids = id_.split(".")
            out = list(filter(lambda c: c.id == ids[0], codes))
            if out:
                pkey = ".".join(ids[1:])
                return self.__extract_code(out[0].codes, pkey)
        else:
            out = list(filter(lambda c: c.id == id_, codes))
            if out:
                return out[0]
        return None

    def __by_id(
        self,
        id: str,
        codes: Sequence[HierarchicalCode],
        out: Optional[Sequence[HierarchicalCode]] = None,
    ) -> Sequence[HierarchicalCode]:
        if out is None:
            out = []
        for i in codes:
            if i.id == id and i not in out:
                out.append(i)  # type: ignore[attr-defined]
            if i.codes:
                self.__by_id(id, i.codes, out)
        return out

    def by_id(self, id: str) -> Sequence[HierarchicalCode]:
        """Get a code without knowing its parent IDs.

        Codes in a hierarchy can be retrieved using their full ID,
        i.e. the code ID, as well as the IDs of their parents in the
        hierarchy, separated by dots (e.g. 1.11.111).

        This function can be used when you just know the code ID,
        and not the ID of its parents.

        Args:
            id: The ID of the code to be returned.

        Returns:
            A set with the matching codes. If there is no matching
            code, the set will be empty. If a code is attached to
            multiple parents, it will be returned only once. As
            hierarchies can reference codes from multiple codelists,
            we could have different codes with the same ID in the
            returned set.
        """
        return self.__by_id(id, self.codes)

    def __get_codes(
        self, codes: Sequence[HierarchicalCode]
    ) -> Sequence[HierarchicalCode]:
        out = []
        for code in codes:
            out.append(code)
            if code.codes:
                out.extend(self.__get_codes(code.codes))
        return out

    def all_codes(self) -> Sequence[HierarchicalCode]:
        """Get all the codes in the hierarchy as a flat list.

        This is useful for validation purposes. The sequence behaves
        as a set, i.e. even if a code is attached to multiple nodes,
        it will be available only once in the returned sequence.

        Returns:
            A flat list of the codes present in the hierarchy.
        """
        out = []
        # We need to do this below because a hierarchical code is not
        # (yet?) hashable.
        for c in self.__get_codes(self.codes):
            if c not in out:
                out.append(c)
        return out


class HierarchyAssociation(
    MaintainableArtefact, frozen=True, omit_defaults=True
):
    """Links a hierarchy to a component withing the context of a dataflow."""

    hierarchy: Optional[Hierarchy] = None
    component_ref: str = ""
    context_ref: str = ""
    operator: Optional[str] = None
