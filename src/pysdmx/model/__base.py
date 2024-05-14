from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.errors import ClientError
from pysdmx.writers.__write_aux import (
    ABBR_COM,
    ABBR_STR,
    add_indent,
    export_intern_data,
)


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
            raise ClientError(
                422,
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


ANNOTATION_WRITER = {
    "title": "AnnotationTitle",
    "type": "AnnotationType",
    "url": "AnnotationURL",
    "text": "AnnotationText",
}


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

    def _to_XML(self, indent: str) -> Any:

        if len(self.annotations) == 0:
            return ""

        child1 = indent
        child2 = add_indent(child1)

        outfile = f"<{ABBR_COM}:Annotations>"
        for annotation in self.annotations:
            if annotation.id is None:
                outfile += f"{child1}<{ABBR_COM}:Annotation>"
            else:
                outfile += (
                    f"{child1}<{ABBR_COM}:Annotation " f"id={annotation.id!r}>"
                )

            for attr, label in ANNOTATION_WRITER.items():
                if getattr(annotation, attr, None) is not None:
                    value = getattr(annotation, attr)
                    value = value.replace("&", "&amp;").rstrip()
                    outfile += (
                        f"{child2}<{ABBR_COM}:{label}>"
                        f"{value}"
                        f"</{ABBR_COM}:{label}>"
                    )

            outfile += f"{child1}</{ABBR_COM}:Annotation>"
        outfile += f"</{ABBR_COM}:Annotations>"
        return outfile


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

    def _to_XML(self, indent: str) -> Dict[str, Any]:
        attributes = ""

        if self.id is not None:
            attributes += f" id={self.id!r}"

        if self.uri is not None:
            attributes += f" uri={self.uri!r}"

        if self.urn is not None:
            attributes += f" urn={self.urn!r}"

        outfile = {
            "Annotations": super(IdentifiableArtefact, self)._to_XML(indent),
            "Attributes": attributes,
        }

        return outfile


class NameableArtefact(IdentifiableArtefact, frozen=True, omit_defaults=True):
    """Nameable Artefact class.

    Provides a name and a description to all derived classes.

    Attributes:
        name: The name of the artefact.
        description: The description of the artefact.
    """

    name: Optional[str] = None
    description: Optional[str] = None

    def _to_XML(self, indent: str) -> Dict[str, Any]:
        outfile = super(NameableArtefact, self)._to_XML(indent)

        if self.name is not None:
            outfile["Name"] = [
                (
                    f"{add_indent(indent)}"
                    f'<{ABBR_COM}:Name xml:lang="en">'
                    f"{self.name}"
                    f"</{ABBR_COM}:Name>"
                )
            ]

        if self.description is not None:
            outfile["Description"] = [
                (
                    f"{add_indent(indent)}"
                    f'<{ABBR_COM}:Description xml:lang="en">'
                    f"{self.description}"
                    f"</{ABBR_COM}:Description>"
                )
            ]

        return outfile


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

    def _to_XML(self, indent: str) -> Dict[str, List[str]]:
        outfile = super(VersionableArtefact, self)._to_XML(indent)

        if self.version is not None:
            outfile["Attributes"] += f" version={self.version!r}"

        if self.valid_from is not None:
            valid_from_str = self.valid_from.strftime("%Y-%m-%dT%H:%M:%S")
            outfile["Attributes"] += f" validFrom={valid_from_str!r}"

        if self.valid_to is not None:
            valid_to_str = self.valid_to.strftime("%Y-%m-%dT%H:%M:%S")
            outfile["Attributes"] += f" validTo={valid_to_str!r}"

        return outfile


class Item(NameableArtefact, frozen=True, omit_defaults=True):
    """Item class.

    The Item is an item of content in an Item Scheme. This may be a
    concept in a concept scheme, a code in a codelist, etc.

    Parent and child attributes (hierarchy) have been removed for simplicity.
    """

    def _to_XML(self, indent: str) -> str:  # type: ignore[override]
        head = type(self).__name__

        if head == "HierarchicalCode":
            head = "Code"

        head = f"{ABBR_STR}:" + head

        data = super(Item, self)._to_XML(indent)
        outfile = f'{indent}<{head}{data["Attributes"]}>'
        outfile += export_intern_data(data, add_indent(indent))
        outfile += f"{indent}</{head}>"
        # if self.parent is not None:
        #     indent_par = add_indent(indent)
        #     indent_ref = add_indent(indent_par)
        #     outfile += f"{indent_par}<{ABBR_STR}:Parent>"
        #     if isinstance(self.parent, Item):
        #         text = self.parent.id
        #     else:
        #         text = self.parent
        #     outfile += f'{indent_ref}<Ref id="{text}"/>'
        #     outfile += f"{indent_par}</{ABBR_STR}:Parent>"
        return outfile


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
            raise ClientError(
                422,
                "Missing agency",
                "Maintainable artefacts must reference an agency.",
            )

    def _to_XML(self, indent: str) -> Dict[str, Any]:
        outfile = super(MaintainableArtefact, self)._to_XML(indent)

        if self.is_external_reference is not None:
            outfile["Attributes"] += (
                f" isExternalReference="
                f"{str(self.is_external_reference).lower()!r}"
            )

        if self.is_final is not None:
            outfile["Attributes"] += f" isFinal={str(self.is_final).lower()!r}"

        if self.agency is not None:
            if isinstance(self.agency, str):
                outfile["Attributes"] += f" agencyID={self.agency!r}"
            else:
                outfile["Attributes"] += f" agencyID={self.agency.id!r}"

        return outfile


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

    def _to_XML(self, indent: str) -> str:  # type: ignore[override]
        """Convert the item scheme to an XML string."""
        indent = add_indent(indent)

        label = f"{ABBR_STR}:{type(self).__name__}"

        data = super(ItemScheme, self)._to_XML(indent)

        if self.is_partial is not None:
            data[
                "Attributes"
            ] += f" isPartial={str(self.is_partial).lower()!r}"

        outfile = ""

        attributes = data.get("Attributes") or None

        if attributes is not None:
            outfile += f"{indent}<{label}{attributes}>"
        else:
            outfile += f"{indent}<{label}>"

        outfile += export_intern_data(data, indent)

        for item in self.items:
            outfile += item._to_XML(add_indent(indent))

        outfile += f"{indent}</{label}>"

        return outfile


class DataflowRef(MaintainableArtefact, frozen=True, omit_defaults=True):
    """Provide core information about a dataflow.

    Attributes:
        id: The dataflow identifier (e.g. BIS_MACRO).
        agency: The organisation (or unit) responsible for the dataflow.
        name: The dataflow name (e.g. MACRO dataflow).
        description: Additional descriptive information about the dataflow.
        version: The version of the dataflow (e.g. 1.0).
    """
