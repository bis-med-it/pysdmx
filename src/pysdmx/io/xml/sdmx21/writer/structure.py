"""Module for writing metadata to XML files."""

from collections import OrderedDict
import re
from typing import Any, Dict, Optional

from pysdmx.io.xml.sdmx21.__parsing_config import (
    AGENCY_ID,
    ATT,
    CL,
    CL_LOW,
    CLASS,
    CON,
    CON_ID,
    CON_LOW,
    CORE_REP,
    DIM,
    DSD,
    DSD_COMPS,
    ENUM,
    FACETS,
    ID,
    LOCAL_REP,
    PACKAGE,
    PAR_ID,
    PAR_VER,
    POSITION,
    PRIM_MEASURE,
    REF,
    TEXT_FORMAT,
    TEXT_TYPE,
    VERSION,
)
from pysdmx.io.xml.sdmx21.reader.__utils import DFW
from pysdmx.io.xml.sdmx21.writer.__write_aux import (
    ABBR_COM,
    ABBR_MSG,
    ABBR_STR,
    add_indent,
    MSG_CONTENT_PKG,
)
from pysdmx.model import Codelist, Concept, DataType, Facets
from pysdmx.model.__base import (
    AnnotableArtefact,
    IdentifiableArtefact,
    Item,
    MaintainableArtefact,
    NameableArtefact,
    VersionableArtefact,
)
from pysdmx.model.dataflow import Component, Dataflow, DataStructureDefinition


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
                if attr == "text":
                    value = __extract_text(value)
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


def __extract_text(item: Dict[str, Any]) -> str:
    text = ""

    if isinstance(item, list) and isinstance(item[0], dict):
        for value in item:
            if value.get("lang") == "en":
                return value.get("#text")
            text = value.get("#text")
        return text

    elif isinstance(item, dict):
        return item.get("#text")

    return item


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


def __write_components(item: DataStructureDefinition, indent: str) -> str:
    """Writes the components to the XML file."""
    outfile = f"{indent}<{ABBR_STR}:{DSD_COMPS}>"
    components: Dict[str, Any] = {
        DIM: [],
        PRIM_MEASURE: [],
        ATT: [],
    }

    for comp in item.components:
        if comp.role == DIM:
            components[DIM].append(comp)
        elif comp.role == ATT:
            components[ATT].append(comp)
        elif comp.role == PRIM_MEASURE:
            components[PRIM_MEASURE].append(comp)

    position = 1
    for _, comps in components.items():
        if comps:
            role_name = comps[0].role.capitalize()
            outfile += f"{add_indent(indent)}<{ABBR_STR}:{role_name}List>"
            for comp in comps:
                outfile += __write_component(
                    comp, position, add_indent(add_indent(indent))
                )
                position += 1
            outfile += f"{add_indent(indent)}</{ABBR_STR}:{role_name}List>"

    outfile += f"{indent}</{ABBR_STR}:{DSD_COMPS}>"
    return outfile


def __write_component(
    item: Component, position, indent: str, CONCEPT=None
) -> str:
    """Writes the component to the XML file."""
    head = f"{indent}<{ABBR_STR}:{item.role.capitalize()} "
    attributes = f"{ID}={item.id} "
    attributes += f"{POSITION}={position} "
    attributes += ">"

    concept_identity = __write_concept_identity(
        item.concept, add_indent(indent)
    )
    representation = __write_representation(item, add_indent(indent))

    outfile = head
    outfile += attributes
    outfile += concept_identity
    outfile += representation
    outfile += f"{indent}</{ABBR_STR}:{item.role.capitalize()}>"
    return outfile


def __write_concept_identity(concept: Concept, indent: str) -> str:
    agency, parent_id, parent_version, id = __extract_urn_data(concept.urn)

    outfile = f"{indent}<{ABBR_STR}:{CON_ID}>"
    outfile += f"{add_indent(indent)}<{ABBR_STR}:{REF} "
    outfile += f'{AGENCY_ID}="{agency!r}" '
    outfile += f"{CLASS}={CON} "
    outfile += f'{ID}="{id!r}" '
    outfile += f'{PAR_ID}="{parent_id!r}" '
    outfile += f'{PAR_VER}="{parent_version!r}" '
    outfile += f'{PACKAGE}="{CON_LOW!r}" '
    outfile += f"{indent}</{ABBR_STR}:{CON_ID}>"

    return outfile


def __write_representation(item: Component, indent: str) -> str:
    representation = local_representation = core_representation = ""

    if item.concept.facets is not None or item.concept.dtype is not None:
        core_representation += __write_text_format(
            item.concept.dtype, item.concept.facets, indent
        )

    if item.concept.codes is not None:
        core_representation += __write_enumeration(item.concept.codes, indent)

    if item.local_facets is not None or item.local_dtype is not None:
        local_representation += __write_text_format(
            item.local_dtype, item.local_facets, indent
        )

    if item.local_codes is not None:
        local_representation += __write_enumeration(item.local_codes, indent)

    if len(core_representation) > 0:
        representation += f"{indent}<{ABBR_STR}:{CORE_REP}>"
        representation += core_representation
        representation += f"{indent}</{ABBR_STR}:{CORE_REP}>"

    if len(local_representation) > 0:
        representation += f"{indent}<{ABBR_STR}:{LOCAL_REP}>"
        representation += local_representation
        representation += f"{indent}</{ABBR_STR}:{LOCAL_REP}>"

    return representation


def __write_text_format(
    dtype: Optional[DataType], facets: Optional[Facets], indent: str
) -> str:
    """Writes the text format to the XML file."""
    outfile = f"{add_indent(indent)}<{ABBR_STR}:{TEXT_FORMAT}"
    if facets is not None:
        active_facets = facets.__str__().replace(",", " ")
        outfile += f" {FACETS}={active_facets!r}"
    if dtype is not None:
        outfile += f" {TEXT_TYPE}={dtype.name!r}"

    outfile += f"{add_indent(indent)}<{ABBR_STR}:{TEXT_FORMAT}>"
    return outfile


def __write_enumeration(codes: Codelist, indent: str) -> str:
    agency, id, version, _ = __extract_urn_data(codes[0].urn)

    outfile = f"{add_indent(indent)}<{ABBR_STR}:{ENUM}>"
    outfile += f"{add_indent(add_indent(indent))}<{ABBR_STR}:{REF} "
    outfile += f'{AGENCY_ID}="{agency!r}" '
    outfile += f"{CLASS}={CL} "
    outfile += f'{ID}="{id!r}" '
    outfile += f'{PACKAGE}="{CL_LOW!r}" '
    outfile += f'{VERSION}="{version!r}"/>'
    outfile += f"{add_indent(indent)}</{ABBR_STR}:{ENUM}>"

    return outfile


def __extract_urn_data(urn: str) -> Any:
    pattern = r"(.+):(.+)\((.+)\)(?:\.(.+))?"

    short_urn = urn.split("=")[-1]
    match = re.match(pattern, short_urn)

    if match is None:
        return "", "", "", ""

    agency, id, version, code_id = match.groups()
    return agency, id, version, code_id


def __write_structure(item: Dataflow, indent: str) -> str:
    """Writes the dataflow structure to the XML file."""
    outfile = f"{indent}<{ABBR_STR}:Structure>"
    outfile += (
        f"{add_indent(indent)}<{REF} "
        f'{PACKAGE}="datastructure" '
        f'{AGENCY_ID}="{item.agency!r}" '
        f'{ID}="{item.id!r}" '
        f'{VERSION}="{item.version!r}" '
        f'{CLASS}="{DSD!r}"/>'.replace("'", "")
    )
    outfile += f"{indent}</{ABBR_STR}:Structure>"
    return outfile


def __write_scheme(item_scheme: Any, indent: str, scheme: str) -> str:
    """Writes the scheme to the XML file."""
    label = f"{ABBR_STR}:{scheme}"

    data = __write_maintainable(item_scheme, indent)

    if scheme == DSD:
        __write_components(item_scheme, add_indent(indent))

    if scheme not in [DSD, DFW]:
        data[
            "Attributes"
        ] += f" isPartial={str(item_scheme.is_final).lower()!r}"

    outfile = ""

    attributes = data.get("Attributes") or ""
    attributes = attributes.replace("'", '"')

    outfile += f"{indent}<{label}{attributes}>"

    outfile += __export_intern_data(data, indent)

    if scheme == DFW:
        outfile += __write_structure(item_scheme, add_indent(indent))

    if scheme not in [DSD, DFW]:
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
        for element in package[key].values():
            item = (
                DSD
                if issubclass(element.__class__, DataStructureDefinition)
                else type(element).__name__
            )
            outfile += __write_scheme(element, add_indent(base_indent), item)
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
