"""Module for writing metadata to XML files."""

from collections import OrderedDict
from typing import Any, Dict

from pysdmx.io.xml.sdmx21.writer.__write_aux import (
    ABBR_COM,
    ABBR_MSG,
    ABBR_STR,
    add_indent,
    MSG_CONTENT_PKG,
)
from pysdmx.model.__base import (
    AnnotableArtefact,
    IdentifiableArtefact,
    Item,
    ItemScheme,
    MaintainableArtefact,
    NameableArtefact,
    VersionableArtefact,
)

ANNOTATION_WRITER = OrderedDict(
    {
        "title": "AnnotationTitle",
        "type": "AnnotationType",
        "text": "AnnotationText",
        "url": "AnnotationURL",
    }
)


def __write_annotable(annotable: AnnotableArtefact, indent: str) -> str:
    """Writes the annotations to the XML file."""
    if len(annotable.annotations) == 0:
        return ""

    child1 = indent
    child2 = add_indent(child1)
    child3 = add_indent(child2)

    outfile = f"{child1}<{ABBR_COM}:Annotations>"
    for annotation in annotable.annotations:
        if annotation.id is None:
            outfile += f"{child2}<{ABBR_COM}:Annotation>"
        else:
            outfile += (
                f"{child2}<{ABBR_COM}:Annotation " f"id={annotation.id!r}>"
            )
        outfile = outfile.replace("'", '"')

        for attr, label in ANNOTATION_WRITER.items():
            if getattr(annotation, attr, None) is not None:
                value = getattr(annotation, attr)
                value = value.replace("&", "&amp;").rstrip()
                if attr == "text":
                    head_tag = f'{ABBR_COM}:{label} xml:lang="en"'
                else:
                    head_tag = f"{ABBR_COM}:{label}"
                outfile += (
                    f"{child3}<{head_tag}>" f"{value}" f"</{ABBR_COM}:{label}>"
                )

        outfile += f"{child2}</{ABBR_COM}:Annotation>"
    outfile += f"{child1}</{ABBR_COM}:Annotations>"
    return outfile


def __write_identifiable(
    identifiable: IdentifiableArtefact, indent: str
) -> Dict[str, Any]:
    """Writes the IdentifiableArtefact to the XML file."""
    attributes = ""

    attributes += f" id={identifiable.id!r}"

    if identifiable.uri is not None:
        attributes += f" uri={identifiable.uri!r}"

    if identifiable.urn is not None:
        attributes += f" urn={identifiable.urn!r}"

    outfile = {
        "Annotations": __write_annotable(identifiable, indent),
        "Attributes": attributes,
    }

    return outfile


def __write_nameable(
    nameable: NameableArtefact, indent: str
) -> Dict[str, Any]:
    """Writes the NameableArtefact to the XML file."""
    outfile = __write_identifiable(nameable, indent)
    attrs = ["Name", "Description"]

    for attr in attrs:
        if getattr(nameable, attr.lower(), None) is not None:
            outfile[attr] = [
                (
                    f"{indent}"
                    f'<{ABBR_COM}:{attr} xml:lang="en">'
                    f"{getattr(nameable, attr.lower())}"
                    f"</{ABBR_COM}:{attr}>"
                )
            ]

    return outfile


def __write_versionable(
    versionable: VersionableArtefact, indent: str
) -> Dict[str, Any]:
    """Writes the VersionableArtefact to the XML file."""
    outfile = __write_nameable(versionable, add_indent(indent))

    outfile["Attributes"] += f" version={versionable.version!r}"

    if versionable.valid_from is not None:
        valid_from_str = versionable.valid_from.strftime("%Y-%m-%dT%H:%M:%S")
        outfile["Attributes"] += f" validFrom={valid_from_str!r}"

    if versionable.valid_to is not None:
        valid_to_str = versionable.valid_to.strftime("%Y-%m-%dT%H:%M:%S")
        outfile["Attributes"] += f" validTo={valid_to_str!r}"

    return outfile


def __write_maintainable(
    maintainable: MaintainableArtefact, indent: str
) -> Dict[str, Any]:
    """Writes the MaintainableArtefact to the XML file."""
    outfile = __write_versionable(maintainable, indent)

    outfile["Attributes"] += (
        f" isExternalReference="
        f"{str(maintainable.is_external_reference).lower()!r}"
    )

    outfile["Attributes"] += f" isFinal={str(maintainable.is_final).lower()!r}"

    if isinstance(maintainable.agency, str):
        outfile["Attributes"] += f" agencyID={maintainable.agency!r}"
    else:
        outfile["Attributes"] += f" agencyID={maintainable.agency.id!r}"

    return outfile


def __write_item(item: Item, indent: str) -> str:
    """Writes the item to the XML file."""
    head = f"{ABBR_STR}:" + type(item).__name__

    data = __write_nameable(item, add_indent(indent))
    attributes = data["Attributes"].replace("'", '"')
    outfile = f"{indent}<{head}{attributes}>"
    outfile += __export_intern_data(data, add_indent(indent))
    outfile += f"{indent}</{head}>"
    return outfile


def __write_item_scheme(item_scheme: ItemScheme, indent: str) -> str:
    """Writes the item scheme to the XML file."""
    label = f"{ABBR_STR}:{type(item_scheme).__name__}"

    data = __write_maintainable(item_scheme, indent)

    data["Attributes"] += f" isPartial={str(item_scheme.is_partial).lower()!r}"

    outfile = ""

    attributes = data.get("Attributes") or ""
    attributes = attributes.replace("'", '"')

    outfile += f"{indent}<{label}{attributes}>"

    outfile += __export_intern_data(data, indent)

    for item in item_scheme.items:
        outfile += __write_item(item, add_indent(indent))

    outfile += f"{indent}</{label}>"

    return outfile


def __write_metadata_element(
    package: Dict[str, Any], key: str, prettyprint: object
) -> str:
    """Writes the metadata element to the XML file.

    Args:
        package: The package to be written
        key: The key to be used
        prettyprint: Prettyprint or not

    Returns:
        A string with the metadata element
    """
    outfile = ""
    nl = "\n" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""

    base_indent = f"{nl}{child2}"

    if key in package:
        outfile += f"{base_indent}<{ABBR_STR}:{MSG_CONTENT_PKG[key]}>"
        for item_scheme in package[key].values():
            outfile += __write_item_scheme(
                item_scheme, add_indent(base_indent)
            )
        outfile += f"{base_indent}</{ABBR_STR}:{MSG_CONTENT_PKG[key]}>"

    return outfile


def __get_outfile(obj_: Dict[str, Any], key: str = "") -> str:
    """Generates an outfile from the object.

    Args:
        obj_: The object to be used
        key: The key to be used

    Returns:
        A string with the outfile

    """
    element = obj_.get(key) or []

    return "".join(element)


def __export_intern_data(data: Dict[str, Any], indent: str) -> str:
    """Export internal data (Annotations, Name, Description) on the XML file.

    Args:
        data: Information to be exported
        indent: Indentation used

    Returns:
        The XML string with the exported data
    """
    outfile = __get_outfile(data, "Annotations")
    outfile += __get_outfile(data, "Name")
    outfile += __get_outfile(data, "Description")

    return outfile


def generate_structures(content: Dict[str, Any], prettyprint: bool) -> str:
    """Writes the structures to the XML file.

    Args:
        content: The Message Content to be written
        prettyprint: Prettyprint or not

    Returns:
        A string with the structures
    """
    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""

    outfile = f"{nl}{child1}<{ABBR_MSG}:Structures>"

    for key in MSG_CONTENT_PKG:
        outfile += __write_metadata_element(content, key, prettyprint)

    outfile += f"{nl}{child1}</{ABBR_MSG}:Structures>"

    return outfile
