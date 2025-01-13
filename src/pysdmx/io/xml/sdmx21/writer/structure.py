"""Module for writing metadata to XML files."""

from collections import OrderedDict
from typing import Any, Dict, Optional, Sequence, Union

from pysdmx.io.xml.enums import MessageType
from pysdmx.io.xml.sdmx21.__tokens import (
    AGENCIES,
    AGENCY_ID,
    AS_STATUS,
    ATT,
    ATT_REL,
    CL,
    CL_LOW,
    CLASS,
    CON,
    CON_ID,
    CONDITIONAL,
    CORE_REP,
    CS,
    DEPARTMENT,
    DFW,
    DIM,
    DSD,
    DSD_COMPS,
    EMAIL,
    ENUM,
    ENUM_FORMAT,
    FAX,
    ID,
    LOCAL_REP,
    MANDATORY,
    MEASURE,
    NAME,
    PACKAGE,
    PAR_ID,
    PAR_VER,
    POSITION,
    PRIM_MEASURE,
    REF,
    ROLE,
    TELEPHONE,
    TEXT_FORMAT,
    TEXT_TYPE,
    TIME_DIM,
    URI,
    URN,
    VERSION,
)
from pysdmx.io.xml.sdmx21.writer.__write_aux import (
    ABBR_COM,
    ABBR_MSG,
    ABBR_STR,
    MSG_CONTENT_PKG,
    __to_lower_camel_case,
    __write_header,
    add_indent,
    create_namespaces,
    get_end_message,
)
from pysdmx.model import (
    AgencyScheme,
    Codelist,
    Concept,
    ConceptScheme,
    DataType,
    Facets,
    Hierarchy,
)
from pysdmx.model.__base import (
    Agency,
    AnnotableArtefact,
    Contact,
    IdentifiableArtefact,
    Item,
    ItemScheme,
    MaintainableArtefact,
    NameableArtefact,
    VersionableArtefact,
)
from pysdmx.model.dataflow import (
    Component,
    Dataflow,
    DataStructureDefinition,
    Role,
)
from pysdmx.model.message import Header
from pysdmx.util import (
    ItemReference,
    parse_item_urn,
    parse_short_urn,
    parse_urn,
)

ANNOTATION_WRITER = OrderedDict(
    {
        "title": "AnnotationTitle",
        "type": "AnnotationType",
        "text": "AnnotationText",
        "url": "AnnotationURL",
    }
)

ROLE_MAPPING = {
    Role.DIMENSION: DIM,
    Role.ATTRIBUTE: ATT,
    Role.MEASURE: PRIM_MEASURE,
}

STR_TYPES = Union[
    ItemScheme,
    Codelist,
    ConceptScheme,
    DataStructureDefinition,
    Dataflow,
]

STR_DICT_TYPE_LIST = {
    AgencyScheme: "OrganisationSchemes",
    Codelist: "Codelists",
    ConceptScheme: "Concepts",
    DataStructureDefinition: "DataStructures",
    Dataflow: "Dataflows",
}


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


def __write_contact(contact: Contact, indent: str) -> str:
    """Writes the contact to the XML file."""

    def __item_to_str(item: Any, ns: str, tag: str) -> str:
        return f"{add_indent(indent)}<{ns}:{tag}>{item}</{ns}:{tag}>"

    def __items_to_str(items: Any, ns: str, tag: str) -> str:
        return "".join([__item_to_str(item, ns, tag) for item in items])

    outfile = f"{indent}<{ABBR_STR}:Contact>"
    if contact.name is not None:
        outfile += __item_to_str(contact.name, ABBR_COM, NAME)
    if contact.department is not None:
        outfile += __item_to_str(contact.department, ABBR_STR, DEPARTMENT)
    if contact.role is not None:
        outfile += __item_to_str(contact.role, ABBR_STR, ROLE)
    if contact.telephones is not None:
        outfile += __items_to_str(contact.telephones, ABBR_STR, TELEPHONE)
    if contact.faxes is not None:
        outfile += __items_to_str(contact.faxes, ABBR_STR, FAX)
    if contact.uris is not None:
        outfile += __items_to_str(contact.uris, ABBR_STR, URI)
    if contact.emails is not None:
        outfile += __items_to_str(contact.emails, ABBR_STR, EMAIL)
    outfile += f"{indent}</{ABBR_STR}:Contact>"

    return outfile


def __write_item(item: Item, indent: str) -> str:
    """Writes the item to the XML file."""
    head = f"{ABBR_STR}:" + type(item).__name__

    data = __write_nameable(item, add_indent(indent))
    attributes = data["Attributes"].replace("'", '"')
    outfile = f"{indent}<{head}{attributes}>"
    outfile += __export_intern_data(data)
    if isinstance(item, Agency) and len(item.contacts) > 0:
        for contact in item.contacts:
            outfile += __write_contact(contact, add_indent(indent))
    if isinstance(item, Concept) and (
        item.codes is not None
        or item.facets is not None
        or item.dtype is not None
    ):
        outfile += f"{add_indent(indent)}<{ABBR_STR}:{CORE_REP}>"
        if item.codes is not None:
            outfile += __write_enumeration(item.codes, add_indent(indent))
        if item.facets is not None or item.dtype is not None:
            outfile += __write_text_format(
                item.dtype, item.facets, TEXT_FORMAT, add_indent(indent)
            )
        outfile += f"{add_indent(indent)}</{ABBR_STR}:{CORE_REP}>"
    outfile += f"{indent}</{head}>"
    return outfile


def __write_components(item: DataStructureDefinition, indent: str) -> str:
    """Writes the components to the XML file."""
    outfile = f"{indent}<{ABBR_STR}:{DSD_COMPS}>"

    components: Dict[str, Any] = {
        DIM: [],
        ATT: [],
        PRIM_MEASURE: [],
    }

    for comp in item.components:
        if comp.role == Role.DIMENSION:
            components[DIM].append(comp)
        elif comp.role == Role.ATTRIBUTE:
            components[ATT].append(comp)
        else:
            components[PRIM_MEASURE].append(comp)

    position = 1
    for _, comps in components.items():
        if comps:
            role_name = ROLE_MAPPING[comps[0].role]
            if role_name == PRIM_MEASURE:
                role_name = MEASURE
            outfile += f"{add_indent(indent)}<{ABBR_STR}:{role_name}List>"
            for comp in comps:
                outfile += __write_component(
                    comp, position, add_indent(add_indent(indent)), components
                )
                position += 1
            outfile += f"{add_indent(indent)}</{ABBR_STR}:{role_name}List>"

    outfile += f"{indent}</{ABBR_STR}:{DSD_COMPS}>"
    return outfile


def __write_attribute_relation(
    item: Component, indent: str, component_info: Dict[str, Any]
) -> str:
    outfile = f"{indent}<{ABBR_STR}:{ATT_REL}>"
    att_rel = item.attachment_level
    if att_rel is None or att_rel == "D":
        outfile += f"{add_indent(indent)}<{ABBR_STR}:None/>"
    else:
        # Check if it is a list of Dimensions or it is related to the
        # primary measure
        if "," in att_rel:
            comps_to_relate = att_rel.split(",")
        elif att_rel == "O":
            comps_to_relate = [component_info[PRIM_MEASURE][0].id]
        else:
            comps_to_relate = [att_rel]

        dim_names = [comp.id for comp in component_info[DIM]]

        for comp_name in comps_to_relate:
            role = Role.DIMENSION if comp_name in dim_names else Role.MEASURE
            related_role = ROLE_MAPPING[role]
            outfile += f"{add_indent(indent)}<{ABBR_STR}:{related_role}>"
            outfile += (
                f"{add_indent(add_indent(indent))}"
                f"<{REF} {ID}={comp_name!r}/>"
            )
            outfile += f"{add_indent(indent)}</{ABBR_STR}:{related_role}>"
    outfile += f"{indent}</{ABBR_STR}:{ATT_REL}>"

    return outfile


def __write_component(
    item: Component, position: int, indent: str, component_info: Dict[str, Any]
) -> str:
    """Writes the component to the XML file."""
    role_name = ROLE_MAPPING[item.role]
    if role_name == DIM and item.id == "TIME_PERIOD":
        role_name = TIME_DIM
    head = f"{indent}<{ABBR_STR}:{role_name} "

    attributes = ""
    attribute_relation = ""
    if item.role == Role.ATTRIBUTE:
        status = MANDATORY if item.required else CONDITIONAL
        attributes += f"{AS_STATUS}={status!r} "
        attribute_relation = __write_attribute_relation(
            item, add_indent(indent), component_info
        )

    attributes += f"{ID}={item.id!r}"
    if item.role == Role.DIMENSION:
        attributes += f" {POSITION}={str(position)!r}"

    if item.urn is not None:
        attributes += f" {URN.lower()}={item.urn!r}"

    attributes += ">"

    concept_identity = __write_concept_identity(
        item.concept, add_indent(indent)
    )
    representation = __write_representation(item, add_indent(indent))

    outfile = head
    outfile += attributes
    outfile += concept_identity
    outfile += representation
    outfile += attribute_relation

    outfile += f"{indent}</{ABBR_STR}:{role_name}>"

    outfile = outfile.replace("'", '"')
    return outfile


def __write_concept_identity(
    identity: Union[Concept, ItemReference], indent: str
) -> str:
    if isinstance(identity, ItemReference):
        ref = identity
    else:
        ref = parse_item_urn(identity.urn)  # type: ignore[arg-type]

    outfile = f"{indent}<{ABBR_STR}:{CON_ID}>"
    outfile += f"{add_indent(indent)}<{REF} "
    outfile += f"{AGENCY_ID}={ref.agency!r} "
    outfile += f"{CLASS}={CON!r} "
    outfile += f"{ID}={ref.item_id!r} "
    outfile += f"{PAR_ID}={ref.id!r} "
    outfile += f"{PAR_VER}={ref.version!r} "
    outfile += f"{PACKAGE}={CS.lower()!r}/>"
    outfile += f"{indent}</{ABBR_STR}:{CON_ID}>"

    outfile = outfile.replace("'", '"')
    return outfile


def __write_representation(item: Component, indent: str) -> str:
    representation = ""
    local_representation = ""

    if item.local_codes is not None:
        local_representation += __write_enumeration(item.local_codes, indent)

    if item.local_facets is not None or item.local_dtype is not None:
        type_ = ENUM_FORMAT if item.local_codes is not None else TEXT_FORMAT
        local_representation += __write_text_format(
            item.local_dtype, item.local_facets, type_, indent
        )

    representation += f"{indent}<{ABBR_STR}:{LOCAL_REP}>"
    if len(local_representation) == 0:
        representation += f"{add_indent(indent)}<{ABBR_STR}:{TEXT_FORMAT}/>"
    representation += local_representation
    representation += f"{indent}</{ABBR_STR}:{LOCAL_REP}>"

    return representation


def __write_text_format(
    dtype: Optional[DataType],
    facets: Optional[Facets],
    type_: str,
    indent: str,
) -> str:
    """Writes the text format to the XML file."""
    outfile = f"{add_indent(indent)}<{ABBR_STR}:{type_}"
    if facets is not None:
        active_facets = facets.__str__().replace("=", '="').split(", ")
        for facet in active_facets:
            facet = __to_lower_camel_case(facet)
            outfile += f' {facet}"'
    if dtype is not None:
        outfile += f" {TEXT_TYPE}={dtype.value!r}"
    outfile += "/>"

    outfile = outfile.replace("'", '"')
    return outfile


def __write_enumeration(codes: Union[Codelist, Hierarchy], indent: str) -> str:
    """Writes the enumeration to the XML file."""
    ref = parse_short_urn(codes.short_urn)

    outfile = f"{add_indent(indent)}<{ABBR_STR}:{ENUM}>"
    outfile += f"{add_indent(add_indent(indent))}<{REF} "
    outfile += f"{AGENCY_ID}={ref.agency!r} "
    outfile += f"{CLASS}={CL!r} "
    outfile += f"{ID}={ref.id!r} "
    outfile += f"{PACKAGE}={CL_LOW!r} "
    outfile += f"{VERSION}={ref.version!r}/>"
    outfile += f"{add_indent(indent)}</{ABBR_STR}:{ENUM}>"

    outfile = outfile.replace("'", '"')
    return outfile


def __write_structure(
    item: Union[DataStructureDefinition, str], indent: str
) -> str:
    """Writes the dataflow structure to the XML file."""
    if isinstance(item, str):
        ref = parse_short_urn(item)
    else:
        ref = parse_urn(item.urn)  # type: ignore[arg-type]
    outfile = f"{indent}<{ABBR_STR}:Structure>"
    outfile += (
        f"{add_indent(indent)}<{REF} "
        f'{PACKAGE}="datastructure" '
        f"{AGENCY_ID}={ref.agency!r} "
        f"{ID}={ref.id!r} "
        f"{VERSION}={ref.version!r} "
        f"{CLASS}={DSD!r}/>"
    )
    outfile += f"{indent}</{ABBR_STR}:Structure>"

    outfile = outfile.replace("'", '"')
    return outfile


def __write_scheme(item_scheme: Any, indent: str, scheme: str) -> str:
    """Writes the scheme to the XML file."""
    label = f"{ABBR_STR}:{scheme}"
    components = ""
    data = __write_maintainable(item_scheme, indent)

    if scheme == DSD:
        components = __write_components(item_scheme, add_indent(indent))

    if scheme not in [DSD, DFW]:
        data["Attributes"] += (
            f" isPartial={str(item_scheme.is_final).lower()!r}"
        )

    outfile = ""

    attributes = data.get("Attributes") or ""
    attributes = attributes.replace("'", '"')

    outfile += f"{indent}<{label}{attributes}>"

    outfile += __export_intern_data(data)

    outfile += components

    if scheme == DFW:
        outfile += __write_structure(item_scheme.structure, add_indent(indent))

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
                else (
                    AGENCIES
                    if element.id == "AGENCIES"
                    else type(element).__name__
                )
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


def __export_intern_data(data: Dict[str, Any]) -> str:
    """Export internal data (Annotations, Name, Description) on the XML file.

    Args:
        data: Information to be exported

    Returns:
        The XML string with the exported data
    """
    outfile = __get_outfile(data, "Annotations")
    outfile += __get_outfile(data, "Name")
    outfile += __get_outfile(data, "Description")

    return outfile


def __write_structures(content: Dict[str, Any], prettyprint: bool) -> str:
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

    # Replace &amp; with & in the outfile
    outfile = outfile.replace("& ", "&amp; ")

    return outfile


def write(
    structures: Sequence[STR_TYPES],
    output_path: str = "",
    prettyprint: bool = True,
    header: Optional[Header] = None,
) -> Optional[str]:
    """This function writes a SDMX-ML file from the Message Content.

    Args:
        structures: The content to be written
        output_path: The path to save the file
        prettyprint: Prettyprint or not
        header: The header to be used (generated if None)

    Returns:
        The XML string if path is empty, None otherwise
    """
    type_ = MessageType.Structure
    elements = {structure.short_urn: structure for structure in structures}
    if header is None:
        header = Header()

    content: Dict[str, Dict[str, STR_TYPES]] = {}
    for urn, element in elements.items():
        list_ = STR_DICT_TYPE_LIST[type(element)]
        if list_ not in content:
            content[list_] = {}
        content[list_][urn] = element

    # Generating the initial tag with namespaces
    outfile = create_namespaces(type_, prettyprint=prettyprint)
    # Generating the header
    outfile += __write_header(header, prettyprint)
    # Writing the content
    outfile += __write_structures(content, prettyprint)

    outfile += get_end_message(type_, prettyprint)

    if output_path == "":
        return outfile

    with open(output_path, "w", encoding="UTF-8", errors="replace") as f:
        f.write(outfile)

    return None
