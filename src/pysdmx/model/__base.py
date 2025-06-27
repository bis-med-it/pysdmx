from datetime import datetime
from typing import Any, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.errors import Invalid


class Annotation(
    Struct, frozen=True, omit_defaults=True, repr_omit_defaults=True
):
    """Annotation class.

    It is used to convey extra information to describe any
    SDMX construct.

    This information may be in the form of a URL reference and/or
    a multilingual text (represented by the association to
    InternationalString).

    Attributes:
        id: The identifier of the annotation.
        title: The title of the annotation.
        type: The type of the annotation.
        url: The URL of the annotation.
        text: The value of the annotation.
    """

    id: Optional[str] = None
    title: Optional[str] = None
    text: Optional[str] = None
    url: Optional[str] = None
    type: Optional[str] = None

    @property
    def value(self) -> Optional[str]:
        """Alias to text."""
        return self.text

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


class AnnotableArtefact(
    Struct,
    frozen=True,
    omit_defaults=True,
    repr_omit_defaults=True,
    kw_only=True,
):
    """Annotable Artefact class.

    Superclass of all SDMX artefacts.
    Contains the list of annotations.

    Attributes:
        annotations: The list of annotations attached to the artefact.
    """

    annotations: Sequence[Annotation] = ()

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # str is taken as a Sequence, so we need to check it's not a str
            if isinstance(value, Sequence) and not isinstance(value, str):
                # Handle non-empty lists
                if value:
                    class_name = value[0].__class__.__name__
                    value = f"{len(value)} {class_name.lower()}s"
                # redundant if check for python 3.9 and lower versions cov
                if not value:
                    continue

            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # Omit empty sequences
            if isinstance(value, (list, tuple, set)) and not value:
                continue
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


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


class Contact(
    Struct, frozen=True, omit_defaults=True, repr_omit_defaults=True
):
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

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # str is taken as a Sequence, so we need to check it's not a str
            if isinstance(value, Sequence) and not isinstance(value, str):
                # Handle non-empty lists
                if not value:
                    continue
                class_name = value[0].__class__.__name__
                value = f"{len(value)} {class_name.lower()}s"

            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # Omit empty sequences
            if isinstance(value, (list, tuple, set)) and not value:
                continue
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


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
    """An organisation that provides data."""


class MetadataProvider(Organisation, frozen=True, omit_defaults=True):
    """An organisation that provides reference metadata."""


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

    @property
    def short_urn(self) -> str:
        """Returns the short URN for the artefact.

        A short URN follows the syntax: Type=Agency:Id(Version). For example:
        Codelist=SDMX:CL_FREQ(1.0)

        Returns:
            The short URN for the artefact.
        """
        agency = (
            self.agency.id if isinstance(self.agency, Agency) else self.agency
        )
        return f"{self.__class__.__name__}={agency}:{self.id}({self.version})"


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


class DataflowRef(
    Struct, frozen=True, omit_defaults=True, repr_omit_defaults=True, tag=True
):
    """A unique reference to a dataflow.

    Attributes:
        id: The dataflow identifier (e.g. BIS_MACRO).
        agency: The organisation (or unit) responsible for the dataflow.
        version: The version of the dataflow (e.g. 1.0).
        name: The name of the dataflow. This is optional as, typically,
            a dataflow reference wouldn't have this information, but it
            has been added as it can be useful in a data discovery
            scenario, for example, in category scheme queries.
    """

    agency: str
    id: str
    version: str = "1.0"
    name: Optional[str] = None

    def __hash__(self) -> int:
        """Returns the dataflow reference's hash."""
        return hash((self.agency, self.id, self.version))

    def __eq__(self, other: Any) -> bool:
        """Whether the 2 objects are equal."""
        return (
            self.__class__ == other.__class__
            and self.agency == other.agency
            and self.id == other.id
            and self.version == other.version
        )

    def __str__(self) -> str:
        """Short_urn representation of the dataflow reference."""
        return f"Dataflow={self.agency}:{self.id}({self.version})"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class Reference(Struct, frozen=True, repr_omit_defaults=True):
    """The coordinates of an SDMX maintainable artefact.

    Attributes:
        sdmx_type: The type of SDMX artefact (``codelist``, etc.)
        agency: The maintainer of the artefact (e.g. ``BIS``, ``SDMX``, etc.)
        id: The artefact ID (e.g. ``CL_FREQ``)
        version: The artefact version (e.g. ``1.0.0``)
    """

    sdmx_type: str
    agency: str
    id: str
    version: str

    def __str__(self) -> str:
        """Returns a string representation of the object."""
        return f"{self.sdmx_type}={self.agency}:{self.id}({self.version})"


class ItemReference(Struct, frozen=True, repr_omit_defaults=True, tag=True):
    """The coordinates of an SDMX non-nested item.

    Attributes:
        sdmx_type: The type of SDMX artefact (``concept``, etc.)
        agency: The maintainer of the artefact (e.g. ``BIS``, etc.)
        id: The maintainable ID (e.g. ``CL_FREQ``)
        version: The artefact version (e.g. ``1.0.0``)
        item_id: The item ID (e.g. ``A``)
    """

    sdmx_type: str
    agency: str
    id: str
    version: str
    item_id: str

    def __str__(self) -> str:
        """Returns a string representation of the object."""
        return (
            f"{self.sdmx_type}={self.agency}:{self.id}"
            f"({self.version}).{self.item_id}"
        )
