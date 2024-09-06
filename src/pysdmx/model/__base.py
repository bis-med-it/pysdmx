from datetime import datetime
from typing import Any, Dict, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.errors import Invalid


class Annotation(Struct, frozen=True, omit_defaults=True):
    """Annotation class.

    It is used to convey extra information to describe any
    SDMX construct.
    This information may be in the form of a URL reference and/or
    a multilingual text (represented by the association to
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

    def __post_init__(self) -> None:
        """Additional validation checks for Annotation."""
        if (
            not self.id
            and not self.title
            and not self.text
            and not self.url
            and not self.type
        ):
            raise Invalid(
                "Empty annotation",
                (
                    "All fields of the annotation have been left empty."
                    "Please set at least one."
                ),
            )

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        out = []
        for k in self.__annotations__.keys():
            v = self.__getattribute__(k)
            if v:
                out.append(f"{k}={str(v)}")
        return ", ".join(out)


class AnnotableArtefact(Struct, frozen=True, omit_defaults=True, kw_only=True):
    """Annotable Artefact class.

    Superclass of all SDMX artefacts.
    Contains the list of annotations.

    Attributes:
        annotations: The list of annotations attached to the artefact.
    """

    annotations: Sequence[Annotation] = ()

    @classmethod
    def __all_annotations(cls) -> Dict[str, Any]:
        class_attributes = {}
        for c in cls.__mro__:
            if "__annotations__" in c.__dict__:
                class_attributes.update(c.__annotations__)
        return dict(reversed(list(class_attributes.items())))

    def __str__(self) -> str:
        """Returns a human-friendly description."""
        out = []
        for k in self.__all_annotations().keys():
            v = self.__getattribute__(k)
            if v:
                out.append(f"{k}={str(v)}")
        return ", ".join(out)


class IdentifiableArtefact(AnnotableArtefact, frozen=True, omit_defaults=True):
    """Identifiable Artefact class.

    Provides identity to all derived classes. It also provides annotations
    to derive classes because it is a subclass of AnnotableArtefact.

    Attributes:
        id: The identifier of the artefact.
        uri: The URI of the artefact.
        urn: The URN of the artefact.
    """

    id: str  # type: ignore[misc, unused-ignore]
    uri: Optional[str] = None
    urn: Optional[str] = None


class NameableArtefact(IdentifiableArtefact, frozen=True, omit_defaults=True):
    """Nameable Artefact class.

    Provides a name and a description to all derived classes.

    Attributes:
        name: The name of the artefact.
        description: The description of the artefact.
    """

    name: Optional[str] = None
    description: Optional[str] = None


class VersionableArtefact(NameableArtefact, frozen=True, omit_defaults=True):
    """Versionable Artefact class.

    Provides a version to all derived classes.

    Attributes:
        version: The version of the artefact.
        valid_from: The date from which the artefact is valid.
        valid_to: The date to which the artefact is valid.
    """

    version: str = "1.0"
    valid_from: Optional[datetime] = None
    valid_to: Optional[datetime] = None


class Item(NameableArtefact, frozen=True, omit_defaults=True):
    """Item class.

    The Item is an item of content in an Item Scheme. This may be a
    concept in a concept scheme, a code in a codelist, etc.

    Parent and child attributes (hierarchy) have been removed for simplicity.
    """


class Contact(Struct, frozen=True, omit_defaults=True):
    """Contact details such as the name of a contact and his email address.

    Attributes:
        id: An identifier for a contact. If the contact represents a person,
            this could be the person's username in the organisation.
        name: The contact name, which could be the name of a person, the name
            of a service ("e.g. Support"), etc.
        department: The department in which the contact is located (e.g.
            "Statistics").
        role: The contact's role, which could be his job title, or a role such
            as data owner, data steward, subject matter expert, etc.
        telephones: A list of telephone numbers.
        faxes: A list of fax numbers.
        uris: A list of URLs relevant for the contact (e.g. a link to an online
            form that can be used to send questions, a link to a support forum,
            etc.).
        emails: a list of email addresses.
    """

    id: Optional[str] = None
    name: Optional[str] = None
    department: Optional[str] = None
    role: Optional[str] = None
    telephones: Optional[Sequence[str]] = None
    faxes: Optional[Sequence[str]] = None
    uris: Optional[Sequence[str]] = None
    emails: Optional[Sequence[str]] = None


class Organisation(Item, frozen=True, omit_defaults=True):
    """Organisation class.

    Attributes:
        contacts: The contact of the agency.
        dataflows: The dataflows relevant for the organisation. For example,
            the list of dataflows for which a data provider provides data.
    """

    contacts: Sequence[Contact] = ()
    dataflows: Sequence["DataflowRef"] = ()

    def __hash__(self) -> int:
        """Returns the organisation's hash."""
        return hash(self.id)


class Agency(Organisation, frozen=True, omit_defaults=True):
    """An organisation that maintains structural metadata.

    This includes statistical classifications, glossaries,
    structural metadata such as Data and Metadata Structure
    Definitions, Concepts and Code lists.
    """


class DataProvider(Organisation, frozen=True, omit_defaults=True):
    """An organisation that provides data or metadata."""


class DataConsumer(Organisation, frozen=True, omit_defaults=True):
    """An organisation that collects data or metadata."""


class MaintainableArtefact(
    VersionableArtefact, frozen=True, omit_defaults=True
):
    """Maintainable Artefact class.

    An abstract class to group together primary structural metadata
    artefacts that are maintained by an Agency.

    Attributes:
        is_final: Whether the artefact is final.
        is_external_reference: Whether the artefact is an external reference.
        service_url: The URL of the service.
        structure_url: The URL of the structure.
        agency: The maintainer of the artefact.
    """

    is_final: bool = False
    is_external_reference: bool = False
    service_url: Optional[str] = None
    structure_url: Optional[str] = None
    agency: Union[str, Agency] = ""

    def __post_init__(self) -> None:
        """Additional validation checks for maintainable artefacts."""
        if not self.agency:
            raise Invalid(
                "Missing agency",
                "Maintainable artefacts must reference an agency.",
            )


class ItemScheme(MaintainableArtefact, frozen=True, omit_defaults=True):
    """ItemScheme class.

    The descriptive information for an arrangement or division of objects
    into groups based on characteristics, which the objects have in common.

    Attributes:
        items: The list of items in the scheme.
        is_partial: Whether the scheme is partial.
    """

    items: Sequence[Item] = ()
    is_partial: bool = False


class DataflowRef(MaintainableArtefact, frozen=True, omit_defaults=True):
    """Provide core information about a dataflow.

    Attributes:
        id: The dataflow identifier (e.g. BIS_MACRO).
        agency: The organisation (or unit) responsible for the dataflow.
        name: The dataflow name (e.g. MACRO dataflow).
        description: Additional descriptive information about the dataflow.
        version: The version of the dataflow (e.g. 1.0).
    """
