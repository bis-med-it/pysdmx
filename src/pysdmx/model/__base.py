from datetime import datetime
from typing import Iterator, Optional, Sequence

from msgspec import Struct


class Annotation(Struct, frozen=True, omit_defaults=True):
    """
    The Annotation is used
    to convey extra information to describe any SDMX construct. This information may be in the
    form of a URL reference and/or a multilingual text (represented by the association to
    InternationalString).

    Attributes:
        id: The identifier of the annotation.
        title: The title of the annotation.
        text: The text of the annotation.
        url: The URL of the annotation.
        type: The type of the annotation.
    """

    id: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        out = ""
        if self.title:
            out += f"{out} - {self.title}"
        if self.text:
            out += f"{out} - {self.text}"
        if self.url:
            out += f"{out} - {self.url}"
        return out


class AnnotableArtefact(Struct, frozen=True, omit_defaults=True):
    """
    Superclass of all SDMX artefacts. Contains the list of annotations.

    Attributes:
        annotations: The list of annotations attached to the artefact.
    """

    annotations: Sequence[Annotation] = ()

    def __iter__(self) -> Iterator[Annotation]:
        """Return an iterator over the list of annotations."""
        yield from self.annotations

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        return f"{self.__class__.__name__}({', '.join(repr(a) for a in self.annotations)})"

    __repr__ = __str__


class IdentifiableArtefact(AnnotableArtefact):
    """
    Provides identity to all derived classes. It also provides annotations
    to derive classes because it is a subclass of AnnotableArtefact.

    Attributes:
        id: The identifier of the artefact.
        uri: The URI of the artefact.
        urn: The URN of the artefact.
    """

    id: str
    uri: Optional[str] = None
    urn: Optional[str] = None

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        return f"{self.__class__.__name__}({self.id}, {', '.join(repr(a) for a in self.annotations)})"

    __repr__ = __str__


class NameableArtefact(IdentifiableArtefact):
    """
    Provides a name and a description to all derived classes.

    Attributes:
        name: The name of the artefact.
        description: The description of the artefact.
    """

    name: Optional[str] = None
    description: Optional[str] = None


class VersionableArtefact(NameableArtefact):
    """
    Provides a version to all derived classes.

    Attributes:
        version: The version of the artefact.
        valid_from: The date from which the artefact is valid.
        valid_to: The date to which the artefact is valid.
    """

    version: str = "1.0"
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class MaintainableArtefact(VersionableArtefact):
    """
    An abstract class to group together primary structural metadata
    artefacts that are maintained by an Agency.

    Attributes:
        is_final: Whether the artefact is final.
        is_external_reference: Whether the artefact is an external reference.
        service_url: The URL of the service.
        structure_url: The URL of the structure.
        maintainer: The maintainer of the artefact.
    """

    is_final: bool = False
    is_external_reference: bool = False
    service_url: str = None
    structure_url: str = None
    maintainer: str = None

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        return f"{self.__class__.__name__}({self.id}, {self.name}, {self.version})"

    __repr__ = __str__


class Agency(MaintainableArtefact):
    """
    Responsible agency for maintaining artefacts such as statistical
    classifications, glossaries, structural metadata such as Data and Metadata Structure
    Definitions, Concepts and Code lists.

    Attributes:
        contacts: The contact of the agency.
    """

    contacts = Sequence["Contact"]


class Item(NameableArtefact):
    """
    The Item is an item of content in an Item Scheme. This may be a
    concept in a concept scheme, a code in a codelist, etc.

    Attributes:
        scheme: The ItemScheme to which the item belongs.
        parent: The parent of the item.
        children: The children of the item.
    """

    scheme: "ItemScheme" = None
    parent: Optional["Item"] = None
    children: Sequence["Item"] = ()


class ItemScheme(MaintainableArtefact):
    """
    The descriptive information for an arrangement or division of objects
    into groups based on characteristics, which the objects have in common.

    Attributes:
        items: The list of items in the scheme.
        is_partial: Whether the scheme is partial.
    """

    items: Sequence["Item"] = ()
    is_partial: bool = False

    def __iter__(self) -> Iterator[Item]:
        """Return an iterator over the list of items."""
        yield from self.items

    def __len__(self) -> int:
        """Return the number of codes in the codelist."""
        return len(self.items)

    def __getitem__(self, id_: str) -> Optional[Item]:
        """Return the code identified by the supplied ID."""
        out = list(filter(lambda item: item.id == id_, self.items))
        if len(out) == 0:
            return None
        else:
            return out[0]
