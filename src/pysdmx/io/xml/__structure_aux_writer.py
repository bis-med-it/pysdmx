"""Module for writing metadata to XML files."""

from collections import OrderedDict
from copy import copy
from typing import Any, Dict, Optional, Sequence, Union

from pysdmx.errors import Invalid
from pysdmx.io.xml.__tokens import (
    AGENCY_ID,
    AGENCY_SCHEME,
    AS_STATUS,
    ATT,
    ATT_REL,
    CL,
    CL_LOW,
    CLASS,
    COMPONENT_MAP,
    CON,
    CON_CONS,
    CON_ID,
    CONDITIONAL,
    CONS_ATT,
    CORE_REP,
    CS,
    CUBE_REGION,
    CUSTOM_TYPE,
    CUSTOM_TYPE_SCHEME,
    DATA_CONS,
    DATA_KEY_SET,
    DATA_PROV,
    DEPARTMENT,
    DFW,
    DIM,
    DIM_REF,
    DSD,
    DSD_COMPS,
    EMAIL,
    ENUM,
    ENUM_FORMAT,
    FAX,
    GROUP,
    GROUP_DIM,
    GROUPS_LOW,
    ID,
    INCLUDE,
    INCLUDED,
    KEY,
    KEY_VALUE,
    LOCAL_REP,
    MANDATORY,
    MANDATORY_LOW,
    MEASURE,
    MEASURE_RELATIONSHIP,
    MSR,
    NAME,
    NAME_PER,
    NAME_PER_SCHEME,
    OPTIONAL_LOW,
    PACKAGE,
    PAR_ID,
    PAR_VER,
    POSITION,
    PROV_AGREEMENT,
    REF,
    REPRESENTATION_MAP,
    ROLE,
    RULE,
    RULE_SCHEME,
    STR_USAGE,
    STRUCTURE_MAP,
    TELEPHONE,
    TEXT_FORMAT,
    TEXT_TYPE,
    TIME_DIM,
    TRANS_SCHEME,
    TRANSFORMATION,
    UDO,
    UDO_SCHEME,
    URI,
    URN,
    URN_LOW,
    USAGE,
    VALUE,
    VALUE_ITEM,
    VALUE_LIST,
    VALUE_LIST_LOW,
    VALUE_LISTS,
    VERSION,
    VTL_MAPPING_SCHEME,
    VTLMAPPING,
)
from pysdmx.io.xml.__write_aux import (
    ABBR_COM,
    ABBR_MSG,
    ABBR_STR,
    MSG_CONTENT_PKG_21,
    MSG_CONTENT_PKG_30,
    __escape_xml,
    __to_lower_camel_case,
    add_indent,
)
from pysdmx.model import (
    AgencyScheme,
    Codelist,
    ComponentMap,
    Concept,
    ConceptScheme,
    ConstraintAttachment,
    CubeRegion,
    CustomType,
    CustomTypeScheme,
    DataConstraint,
    DataType,
    DatePatternMap,
    Facets,
    FixedValueMap,
    Hierarchy,
    ImplicitComponentMap,
    KeySet,
    MultiComponentMap,
    MultiValueMap,
    NamePersonalisation,
    NamePersonalisationScheme,
    RepresentationMap,
    Ruleset,
    RulesetScheme,
    StructureMap,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    ValueMap,
    VtlCodelistMapping,
    VtlConceptMapping,
    VtlDataflowMapping,
    VtlMappingScheme,
    VtlScheme,
)
from pysdmx.model.__base import (
    Agency,
    AnnotableArtefact,
    Contact,
    IdentifiableArtefact,
    Item,
    ItemReference,
    ItemScheme,
    MaintainableArtefact,
    NameableArtefact,
    Reference,
    VersionableArtefact,
)
from pysdmx.model.dataflow import (
    Component,
    Dataflow,
    DataStructureDefinition,
    Group,
    ProvisionAgreement,
    Role,
)
from pysdmx.util import (
    parse_item_urn,
    parse_short_item_urn,
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
    Role.MEASURE: MEASURE,
}

STR_TYPES = Union[
    ItemScheme,
    Codelist,
    ConceptScheme,
    DataStructureDefinition,
    Dataflow,
    CustomTypeScheme,
    VtlMappingScheme,
    NamePersonalisationScheme,
    RulesetScheme,
    UserDefinedOperatorScheme,
    TransformationScheme,
]

STR_DICT_TYPE_LIST_21 = {
    AgencyScheme: "OrganisationSchemes",
    Codelist: "Codelists",
    ConceptScheme: "Concepts",
    DataStructureDefinition: "DataStructures",
    Dataflow: "Dataflows",
    DataConstraint: "Constraints",
    RepresentationMap: "RepresentationMaps",
    StructureMap: "StructureMaps",
    DatePatternMap: "DatePatternMaps",
    CustomTypeScheme: "CustomTypes",
    VtlMappingScheme: "VtlMappings",
    NamePersonalisationScheme: "NamePersonalisations",
    RulesetScheme: "Rulesets",
    UserDefinedOperatorScheme: "UserDefinedOperators",
    TransformationScheme: "Transformations",
    ProvisionAgreement: "ProvisionAgreements",
}


STR_DICT_TYPE_LIST_30 = {
    AgencyScheme: "AgencySchemes",
    Codelist: "Codelists",
    ConceptScheme: "ConceptSchemes",
    DataStructureDefinition: "DataStructures",
    Dataflow: "Dataflows",
    DataConstraint: "DataConstraints",
    RepresentationMap: "RepresentationMaps",
    StructureMap: "StructureMaps",
    DatePatternMap: "DatePatternMaps",
    CustomTypeScheme: "CustomTypeSchemes",
    VtlMappingScheme: "VtlMappingSchemes",
    NamePersonalisationScheme: "NamePersonalisationSchemes",
    RulesetScheme: "RulesetSchemes",
    UserDefinedOperatorScheme: "UserDefinedOperatorSchemes",
    TransformationScheme: "TransformationSchemes",
    ProvisionAgreement: "ProvisionAgreements",
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
            outfile += f"{child2}<{ABBR_COM}:Annotation id={annotation.id!r}>"
        outfile = outfile.replace("'", '"')

        for attr, label in ANNOTATION_WRITER.items():
            if getattr(annotation, attr, None) is not None:
                value = getattr(annotation, attr)
                value = __escape_xml(str(value))

                if attr == "text":
                    head_tag = f'{ABBR_COM}:{label} xml:lang="en"'

                else:
                    head_tag = f"{ABBR_COM}:{label}"

                outfile += f"{child3}<{head_tag}>{value}</{ABBR_COM}:{label}>"

        outfile += f"{child2}</{ABBR_COM}:Annotation>"
    outfile += f"{child1}</{ABBR_COM}:Annotations>"
    return outfile


def __write_identifiable(
    identifiable: IdentifiableArtefact,
    indent: str,
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
        value = getattr(nameable, attr.lower(), None)
        if value is not None:
            value = __escape_xml(str(value))
            outfile[attr] = [
                (
                    f"{indent}"
                    f'<{ABBR_COM}:{attr} xml:lang="en">'
                    f"{value}"
                    f"</{ABBR_COM}:{attr}>"
                )
            ]
        elif attr == "Name":
            raise Invalid(
                f"Name is required for NameableArtefact id= {nameable.id}"
            )

    return outfile


def __write_versionable(
    versionable: VersionableArtefact, indent: str, references_30: bool = False
) -> Dict[str, Any]:
    """Writes the VersionableArtefact to the XML file."""
    outfile = __write_nameable(versionable, add_indent(indent))

    if not (references_30 and isinstance(versionable, AgencyScheme)):
        outfile["Attributes"] += f" version={versionable.version!r}"

    if versionable.valid_from is not None:
        valid_from_str = versionable.valid_from.strftime("%Y-%m-%dT%H:%M:%S")
        outfile["Attributes"] += f" validFrom={valid_from_str!r}"

    if versionable.valid_to is not None:
        valid_to_str = versionable.valid_to.strftime("%Y-%m-%dT%H:%M:%S")
        outfile["Attributes"] += f" validTo={valid_to_str!r}"

    return outfile


def __write_maintainable(
    maintainable: MaintainableArtefact,
    indent: str,
    references_30: bool = False,
) -> Dict[str, Any]:
    """Writes the MaintainableArtefact to the XML file."""
    outfile = __write_versionable(maintainable, indent, references_30)

    outfile["Attributes"] += (
        f" isExternalReference="
        f"{str(maintainable.is_external_reference).lower()!r}"
    )
    if not references_30 and not (isinstance(maintainable, AgencyScheme)):
        outfile["Attributes"] += (
            f" isFinal={str(maintainable.is_final).lower()!r}"
        )

    if isinstance(maintainable.agency, str):
        outfile["Attributes"] += f" agencyID={maintainable.agency!r}"
    else:
        outfile["Attributes"] += f" agencyID={maintainable.agency.id!r}"

    return outfile


def __write_contact(contact: Contact, indent: str) -> str:
    """Writes the contact to the XML file."""

    def __item_to_str(item: Any, ns: str, tag: str) -> str:
        return (
            f"{add_indent(indent)}"
            f"<{ns}:{tag}>"
            f"{__escape_xml(str(item))}"
            f"</{ns}:{tag}>"
        )

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


def __write_item(
    item: Item, indent: str, scheme: str, references_30: bool = False
) -> str:
    """Writes the item to the XML file."""
    item_name = VALUE_ITEM if scheme == VALUE_LIST else type(item).__name__
    head = f"{ABBR_STR}:" + item_name

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
        format_enum_text = TEXT_FORMAT
        if item.codes is not None:
            format_enum_text = ENUM_FORMAT
            outfile += __write_enumeration(
                item.codes, add_indent(indent), references_30
            )
        if item.facets is not None or item.dtype is not None:
            outfile += __write_text_format(
                item.dtype, item.facets, format_enum_text, add_indent(indent)
            )
        outfile += f"{add_indent(indent)}</{ABBR_STR}:{CORE_REP}>"
    outfile += f"{indent}</{head}>"
    return outfile


def __write_groups(
    groups: list[Group], indent: str, references_30: bool = False
) -> str:
    out_file = ""
    for group in groups:
        out_file += (
            f"{indent}<{ABBR_STR}:{GROUP} {URN_LOW}={group.urn!r}"
            f" {ID}={group.id!r}>"
        )
        for dimension in group.dimensions:
            if references_30:
                out_file += (
                    f"{add_indent(indent)}"
                    f"<{ABBR_STR}:{GROUP_DIM}>"
                    f"{add_indent(add_indent(indent))}"
                    f"<{ABBR_STR}:{DIM_REF}>{dimension}</{ABBR_STR}:{DIM_REF}>"
                    f"{add_indent(indent)}</{ABBR_STR}:{GROUP_DIM}>"
                )
            else:
                out_file += (
                    f"{add_indent(indent)}"
                    f"<{ABBR_STR}:{GROUP_DIM}>"
                    f"{add_indent(add_indent(indent))}"
                    f"<{ABBR_STR}:{DIM_REF}>"
                    f"{add_indent(add_indent(add_indent(indent)))}"
                    f"<{REF} {ID}={dimension!r}/>"
                    f"{add_indent(add_indent(indent))}"
                    f"</{ABBR_STR}:{DIM_REF}>"
                    f"{add_indent(add_indent(indent))}</{ABBR_STR}:{GROUP_DIM}>"
                )

        out_file += f"{indent}</{ABBR_STR}:{GROUP}>"
        out_file = out_file.replace("'", '"')
    return out_file


def __write_components(  # noqa: C901
    dsd: DataStructureDefinition, indent: str, references_30: bool = False
) -> str:
    """Writes the components to the XML file."""
    outfile = f"{indent}<{ABBR_STR}:{DSD_COMPS}>"

    components: Dict[str, Any] = {
        DIM: [],
        ATT: [],
        MEASURE: [],
    }
    out_group = ""
    groups = getattr(dsd, GROUPS_LOW, [])
    if groups is not None and len(groups) > 0:
        out_group = __write_groups(groups, add_indent(indent), references_30)

    for comp in dsd.components:
        if comp.role == Role.DIMENSION:
            components[DIM].append(comp)
        elif comp.role == Role.ATTRIBUTE:
            components[ATT].append(comp)
        else:
            components[MEASURE].append(comp)

    if not references_30 and len(components[MEASURE]) > 1:
        raise Invalid(
            title="Request cannot be fulfilled",
            description=f"SDMX-ML 2.1 does not support multiple measures. "
            f"Check the {dsd.short_urn}.",
            csi={
                "measures_found": components[MEASURE],
            },
        )

    position = 1
    for comps in components.values():
        if comps:
            role_name = ROLE_MAPPING[comps[0].role]
            if role_name == MEASURE:
                role_name = MSR
            outfile += f"{add_indent(indent)}<{ABBR_STR}:{role_name}List>"
            for comp in comps:
                outfile += __write_component(
                    comp,
                    position,
                    add_indent(add_indent(indent)),
                    components,
                    groups,
                    references_30,
                )
                position += 1
            outfile += f"{add_indent(indent)}</{ABBR_STR}:{role_name}List>"
            if role_name == DIM:
                outfile += out_group

    outfile += f"{indent}</{ABBR_STR}:{DSD_COMPS}>"
    return outfile


def __find_matching_group_id(
    att_rel: str, groups: list[Group]
) -> Optional[str]:
    comps_to_relate = att_rel.split(",") if "," in att_rel else [att_rel]
    for group in groups:
        if set(comps_to_relate) == set(group.dimensions):
            return group.id
    return None


def __comps_to_relate(
    att_rel: str,
    component_info: Dict[str, Any],
    references_30: bool = False,
) -> list[str]:
    if "," in att_rel:
        comps_to_relate = att_rel.split(",")
    elif att_rel == "O":
        if references_30:
            comps_to_relate = []
            for measure in component_info[MEASURE]:
                comps_to_relate.append(measure)
        else:
            comps_to_relate = [component_info[MEASURE][0].id]
    else:
        comps_to_relate = [att_rel]
    return comps_to_relate


def __write_attribute_relation(  # noqa: C901
    item: Component,
    indent: str,
    component_info: Dict[str, Any],
    groups: list[Group],
    references_30: bool = False,
) -> str:
    measure_relationship = ""
    outfile = f"{indent}<{ABBR_STR}:{ATT_REL}>"
    # At this point an attribute relation is always
    # present due to the post_init check in Component
    att_rel: str = item.attachment_level  # type: ignore[assignment]
    # Check if it is a list of Dimensions or it is related to the
    # primary measure
    group_id = None
    if groups is not None:
        group_id = __find_matching_group_id(att_rel, groups)
    comps_to_relate = __comps_to_relate(att_rel, component_info, references_30)
    dim_names = [comp.id for comp in component_info[DIM]]
    if references_30:
        if att_rel == "O":
            outfile += f"{add_indent(indent)}<{ABBR_STR}:Observation/>"
            measure_relationship += (
                f"{indent}<{ABBR_STR}:{MEASURE_RELATIONSHIP}>"
            )
            for comp_name in comps_to_relate:
                measure_relationship += (
                    f"{add_indent(indent)}<{ABBR_STR}:{MSR}>"
                    f"{comp_name.id}</{ABBR_STR}:{MSR}>"  # type: ignore[attr-defined]
                )
            measure_relationship += (
                f"{indent}</{ABBR_STR}:{MEASURE_RELATIONSHIP}>"
            )

        elif att_rel == "D":
            outfile += f"{add_indent(indent)}<{ABBR_STR}:Dataflow/>"
        elif group_id is not None:
            outfile += (
                f"{add_indent(indent)}<{ABBR_STR}:{GROUP}>"
                f"{group_id}</{ABBR_STR}:{GROUP}>"
            )
        else:
            is_dimension = comps_to_relate[0] in dim_names
            if is_dimension:
                for comp_name in comps_to_relate:
                    outfile += (
                        f"{add_indent(indent)}<{ABBR_STR}:{DIM}>"
                        f"{comp_name}</{ABBR_STR}:{DIM}>"
                    )
            else:
                outfile += f"{add_indent(indent)}<{ABBR_STR}:Observation/>"
                measure_relationship += (
                    f"{indent}<{ABBR_STR}:{MEASURE_RELATIONSHIP}>"
                )
                for comp_name in comps_to_relate:
                    measure_relationship += (
                        f"{add_indent(indent)}<{ABBR_STR}:{MSR}>"
                        f"{comp_name}</{ABBR_STR}:{MSR}>"
                    )
                measure_relationship += (
                    f"{indent}</{ABBR_STR}:{MEASURE_RELATIONSHIP}>"
                )

    else:
        if group_id is not None:
            outfile += (
                f"{add_indent(indent)}<{ABBR_STR}:{GROUP}>"
                f"{add_indent(add_indent(indent))}<{REF} "
                f"{ID}={group_id!r}/>"
                f"{add_indent(indent)}</{ABBR_STR}:{GROUP}>"
            )
        elif att_rel == "D":
            outfile += f"{add_indent(indent)}<{ABBR_STR}:None/>"

        else:
            for comp_name in comps_to_relate:
                role = (
                    Role.DIMENSION if comp_name in dim_names else Role.MEASURE
                )
                related_role = ROLE_MAPPING[role]
                outfile += f"{add_indent(indent)}<{ABBR_STR}:{related_role}>"
                outfile += (
                    f"{add_indent(add_indent(indent))}"
                    f"<{REF} {ID}={comp_name!r}/>"
                )
                outfile += f"{add_indent(indent)}</{ABBR_STR}:{related_role}>"

    outfile += f"{indent}</{ABBR_STR}:{ATT_REL}>"
    if measure_relationship:
        outfile += measure_relationship

    return outfile


def __write_component(
    item: Component,
    position: int,
    indent: str,
    component_info: Dict[str, Any],
    groups: list[Group],
    references_30: bool = False,
) -> str:
    """Writes the component to the XML file."""
    role_name = ROLE_MAPPING[item.role]
    if role_name == DIM and item.id == "TIME_PERIOD":
        role_name = TIME_DIM
    if references_30 and role_name == MEASURE:
        role_name = MSR

    head = f"{indent}<{ABBR_STR}:{role_name} "

    attributes = ""
    attribute_relation = ""
    if item.role == Role.ATTRIBUTE:
        if references_30:
            status = MANDATORY_LOW if item.required else OPTIONAL_LOW
            attributes += f"{USAGE}={status!r} "
        else:
            status = MANDATORY if item.required else CONDITIONAL
            attributes += f"{AS_STATUS}={status!r} "
        attribute_relation = __write_attribute_relation(
            item, add_indent(indent), component_info, groups, references_30
        )

    attributes += f"{ID}={item.id!r}"
    if item.role == Role.DIMENSION and not (
        role_name == TIME_DIM and references_30
    ):
        attributes += f" {POSITION}={str(position)!r}"

    if item.urn is not None:
        urn = item.urn
        if item.role == Role.MEASURE:
            # Handling URN to ensure roundtrip between SDMX 2.1 and 3.0
            if references_30:
                urn = urn.replace(".PrimaryMeasure", ".Measure")
            else:
                urn = urn.replace(".Measure", ".PrimaryMeasure")
        attributes += f" {URN.lower()}={urn!r}"

    attributes += ">"

    concept_identity = __write_concept_identity(
        item.concept, add_indent(indent), references_30
    )
    representation = __write_representation(
        item, add_indent(indent), references_30
    )

    outfile = head
    outfile += attributes
    outfile += concept_identity
    outfile += representation
    outfile += attribute_relation

    outfile += f"{indent}</{ABBR_STR}:{role_name}>"

    outfile = outfile.replace("'", '"')
    return outfile


def __write_concept_identity(
    identity: Union[Concept, ItemReference],
    indent: str,
    references_30: bool = False,
) -> str:
    if isinstance(identity, ItemReference):
        ref = identity
    elif identity.urn is not None:
        ref = parse_item_urn(identity.urn)
    else:
        raise Invalid(
            f"Cannot select concept identity without URN. "
            f"Concept id={identity.id!r}"
        )

    outfile = f"{indent}<{ABBR_STR}:{CON_ID}>"
    if references_30:
        outfile += (
            f"urn:sdmx:org.sdmx.infomodel.conceptscheme.{ref.sdmx_type}={ref.agency}:"
            f"{ref.id}({ref.version}).{ref.item_id}"
            f"</{ABBR_STR}:{CON_ID}>"
        )
    else:
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


def __write_representation(
    item: Component, indent: str, references_30: bool = False
) -> str:
    representation = ""
    local_representation = ""

    if item.local_codes is not None:
        local_representation += __write_enumeration(
            item.local_codes, indent, references_30
        )

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
        # Writing only facets not using default values
        active_facets = facets.__rich_repr__()
        for facet, value, *_ in active_facets:  # type: ignore[misc]
            facet = __to_lower_camel_case(facet)
            outfile += f' {facet}="{value}"'
    if dtype is not None:
        outfile += f" {TEXT_TYPE}={dtype.value!r}"
    outfile += "/>"

    outfile = outfile.replace("'", '"')
    return outfile


def __write_enumeration(
    codes: Union[Codelist, Hierarchy], indent: str, references_30: bool = False
) -> str:
    """Writes the enumeration to the XML file."""
    ref = parse_short_urn(codes.short_urn)
    outfile = f"{add_indent(indent)}<{ABBR_STR}:{ENUM}>"
    if references_30:
        outfile += (
            f"urn:sdmx:org.sdmx.infomodel.codelist.{ref.sdmx_type}={ref.agency}:{ref.id}({ref.version})"
            f"</{ABBR_STR}:{ENUM}>"
        )
    else:
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
    item: str, indent: str, references_30: bool = False
) -> str:
    """Writes the dataflow structure to the XML file."""
    ref = parse_short_urn(item)
    outfile = f"{indent}<{ABBR_STR}:Structure>"
    if references_30:
        outfile += (
            f"urn:sdmx:org.sdmx.infomodel.datastructure.{DSD}={ref.agency}:{ref.id}({ref.version})"
            f"</{ABBR_STR}:Structure>"
        )
    else:
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


def __write_prov_agreement(
    dataflow: str, provider: str, indent: str, references_30: bool = False
) -> str:
    """Writes the provision agreement structure to the XML file."""
    ref_df = parse_short_urn(dataflow)
    ref_pr = parse_short_item_urn(provider)
    if references_30:
        outfile = f"{indent}<{ABBR_STR}:{DFW}>"
        outfile += (
            f"urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow={ref_df.agency}:{ref_df.id}({ref_df.version})"
            f"</{ABBR_STR}:{DFW}>"
        )
        outfile += f"{indent}<{ABBR_STR}:{DATA_PROV}>"
        outfile += (
            f"urn:sdmx:org.sdmx.infomodel.base.DataProvider={ref_pr.agency}:{ref_pr.id}({ref_pr.version}).{ref_pr.item_id}"
            f"</{ABBR_STR}:{DATA_PROV}>"
        )
    else:
        outfile = f"{indent}<{ABBR_STR}:{STR_USAGE}>"
        outfile += (
            f"{add_indent(indent)}<{REF} "
            f'{PACKAGE}="datastructure" '
            f"{AGENCY_ID}={ref_df.agency!r} "
            f"{ID}={ref_df.id!r} "
            f"{VERSION}={ref_df.version!r} "
            f"{CLASS}={DFW!r}/>"
        )
        outfile += f"{indent}</{ABBR_STR}:{STR_USAGE}>"
        outfile += f"{indent}<{ABBR_STR}:{DATA_PROV}>"
        outfile += (
            f"{add_indent(indent)}<{REF} "
            f"{PAR_ID}={ref_pr.id!r} "
            f'{PACKAGE}="base" '
            f"{PAR_VER}={ref_pr.version!r} "
            f"{AGENCY_ID}={ref_pr.agency!r} "
            f"{ID}={ref_pr.item_id!r} "
            f"{CLASS}={DATA_PROV!r}/>"
        )
        outfile += f"{indent}</{ABBR_STR}:{DATA_PROV}>"

    outfile = outfile.replace("'", '"')
    return outfile


def __write_value_map(
    value_map: Union[ValueMap, MultiValueMap], indent: str
) -> str:
    """Writes a ValueMap or MultiValueMap (RepresentationMapping)."""
    outfile = f"{indent}<{ABBR_STR}:RepresentationMapping>"

    # MultiValueMap
    if isinstance(value_map, MultiValueMap):
        for s in value_map.source:
            outfile += (
                f"{add_indent(indent)}<{ABBR_STR}:SourceValue>"
                f"{__escape_xml(str(s))}"
                f"</{ABBR_STR}:SourceValue>"
            )
        for t in value_map.target:
            outfile += (
                f"{add_indent(indent)}<{ABBR_STR}:TargetValue>"
                f"{__escape_xml(str(t))}"
                f"</{ABBR_STR}:TargetValue>"
            )
        outfile += f"{indent}</{ABBR_STR}:RepresentationMapping>"
        return outfile

    # ValueMap
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:SourceValue>"
        f"{__escape_xml(str(value_map.source))}"
        f"</{ABBR_STR}:SourceValue>"
    )
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:TargetValue>"
        f"{__escape_xml(str(value_map.target))}"
        f"</{ABBR_STR}:TargetValue>"
    )
    outfile += f"{indent}</{ABBR_STR}:RepresentationMapping>"
    return outfile


def __write_multi_component_map(
    comp_map: MultiComponentMap, indent: str
) -> str:
    """Writes a MultiComponentMap (1-n, n-1, n-n) to the XML file."""
    outfile = f"{indent}<{ABBR_STR}:{COMPONENT_MAP}>"

    for s in comp_map.source:
        outfile += (
            f"{add_indent(indent)}<{ABBR_STR}:Source>"
            f"{__escape_xml(str(s))}"
            f"</{ABBR_STR}:Source>"
        )

    for t in comp_map.target:
        outfile += (
            f"{add_indent(indent)}<{ABBR_STR}:Target>"
            f"{__escape_xml(str(t))}"
            f"</{ABBR_STR}:Target>"
        )

    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:RepresentationMap>"
        f"{__escape_xml(str(comp_map.values))}"
        f"</{ABBR_STR}:RepresentationMap>"
    )

    outfile += f"{indent}</{ABBR_STR}:{COMPONENT_MAP}>"
    return outfile


def __write_representation_map(
    rep_map: RepresentationMap, indent: str, references_30: bool = False
) -> str:
    """Writes a RepresentationMap to the XML file."""
    data = __write_maintainable(rep_map, indent, references_30)

    label = f"{ABBR_STR}:{REPRESENTATION_MAP}"
    attributes = data.get("Attributes") or ""
    attributes = attributes.replace("'", '"')

    outfile = f"{indent}<{label}{attributes}>"
    outfile += __export_intern_data(data)

    # Write Source and Target references
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:SourceCodelist>"
        f"{rep_map.source}"
        f"</{ABBR_STR}:SourceCodelist>"
    )
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:TargetCodelist>"
        f"{rep_map.target}"
        f"</{ABBR_STR}:TargetCodelist>"
    )

    # Write ValueMaps
    for value_map in rep_map.maps:
        outfile += __write_value_map(value_map, add_indent(indent))

    outfile += f"{indent}</{label}>"

    return outfile


def __write_component_map(
    comp_map: ComponentMap, indent: str, references_30: bool = False
) -> str:
    """Writes a ComponentMap to the XML file."""
    outfile = f"{indent}<{ABBR_STR}:{COMPONENT_MAP}>"
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Source>"
        f"{comp_map.source}"
        f"</{ABBR_STR}:Source>"
    )
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Target>"
        f"{comp_map.target}"
        f"</{ABBR_STR}:Target>"
    )

    # Write the RepresentationMap reference
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:RepresentationMap>"
        f"{comp_map.values}"
        f"</{ABBR_STR}:RepresentationMap>"
    )

    outfile += f"{indent}</{ABBR_STR}:{COMPONENT_MAP}>"
    return outfile


def __write_implicit_component_map(
    imp_comp_map: ImplicitComponentMap, indent: str
) -> str:
    """Writes an ImplicitComponentMap (no RepresentationMap)."""
    outfile = f"{indent}<{ABBR_STR}:ComponentMap>"
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Source>"
        f"{imp_comp_map.source}"
        f"</{ABBR_STR}:Source>"
    )
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Target>"
        f"{imp_comp_map.target}"
        f"</{ABBR_STR}:Target>"
    )
    outfile += f"{indent}</{ABBR_STR}:ComponentMap>"
    return outfile


def __write_fixed_value_map(fixed_map: FixedValueMap, indent: str) -> str:
    """Writes a FixedValueMap to the XML file."""
    outfile = f"{indent}<{ABBR_STR}:FixedValueMap>"
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Target>"
        f"{fixed_map.target}"
        f"</{ABBR_STR}:Target>"
    )
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Value>"
        f"{__escape_xml(str(fixed_map.value))}"
        f"</{ABBR_STR}:Value>"
    )
    outfile += f"{indent}</{ABBR_STR}:FixedValueMap>"
    return outfile


def __write_date_pattern_map(date_map: DatePatternMap, indent: str) -> str:
    """Writes a DatePatternMap to the XML file."""
    attrs = ""
    if date_map.id is not None:
        attrs += f' id="{__escape_xml(date_map.id)}"'
    if date_map.resolve_period is not None:
        attrs += f' resolvePeriod="{__escape_xml(date_map.resolve_period)}"'

    attrs += f' sourcePattern="{__escape_xml(date_map.pattern)}"'
    attrs += f' locale="{__escape_xml(date_map.locale)}"'

    outfile = f"{indent}<{ABBR_STR}:DatePatternMap{attrs}>"
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Source>"
        f"{__escape_xml(date_map.source)}"
        f"</{ABBR_STR}:Source>"
    )
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Target>"
        f"{__escape_xml(date_map.target)}"
        f"</{ABBR_STR}:Target>"
    )

    if date_map.pattern_type == "variable":
        outfile += (
            f"{add_indent(indent)}<{ABBR_STR}:FrequencyDimension>"
            f"{__escape_xml(date_map.frequency)}"
            f"</{ABBR_STR}:FrequencyDimension>"
        )
    else:
        outfile += (
            f"{add_indent(indent)}<{ABBR_STR}:TargetFrequencyID>"
            f"{__escape_xml(date_map.frequency)}"
            f"</{ABBR_STR}:TargetFrequencyID>"
        )

    outfile += f"{indent}</{ABBR_STR}:DatePatternMap>"
    return outfile


def __write_structure_map(
    struct_map: StructureMap, indent: str, references_30: bool = False
) -> str:
    """Writes a StructureMap to the XML file."""
    data = __write_maintainable(struct_map, indent, references_30)

    label = f"{ABBR_STR}:{STRUCTURE_MAP}"
    attributes = data.get("Attributes") or ""
    attributes = attributes.replace("'", '"')

    outfile = f"{indent}<{label}{attributes}>"
    outfile += __export_intern_data(data)

    # Write Source and Target references
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Source>"
        f"{struct_map.source}"
        f"</{ABBR_STR}:Source>"
    )
    outfile += (
        f"{add_indent(indent)}<{ABBR_STR}:Target>"
        f"{struct_map.target}"
        f"</{ABBR_STR}:Target>"
    )

    # Write component maps and fixed value maps
    for map_item in struct_map.maps:
        if isinstance(map_item, DatePatternMap):
            outfile += __write_date_pattern_map(map_item, add_indent(indent))
    for map_item in struct_map.maps:
        if isinstance(map_item, MultiComponentMap):
            outfile += __write_multi_component_map(
                map_item, add_indent(indent)
            )
        elif isinstance(map_item, ComponentMap):
            outfile += __write_component_map(
                map_item, add_indent(indent), references_30
            )
        elif isinstance(map_item, ImplicitComponentMap):
            outfile += __write_implicit_component_map(
                map_item, add_indent(indent)
            )
        if isinstance(map_item, FixedValueMap):
            outfile += __write_fixed_value_map(map_item, add_indent(indent))

    outfile += f"{indent}</{label}>"

    return outfile


def __write_data_provider(
    data_provider: str, indent: str, references_30: bool = False
) -> str:
    """Writes a DataProvider reference to the XML file."""
    outfile = f"{add_indent(indent)}<{ABBR_STR}:DataProvider>"
    if references_30:
        # SDMX 3.0: URN
        outfile += data_provider
    else:
        # SDMX 2.1: Ref with attributes
        outfile += f"{add_indent(add_indent(indent))}<{REF} "
        ref = parse_urn(data_provider)
        outfile += f"{AGENCY_ID}={ref.agency!r} "
        outfile += f"{PAR_ID}={ref.id!r} "
        outfile += f"{PAR_VER}={ref.version!r} "
        outfile += f"{ID}={ref.item_id!r} "
        outfile += f"{CLASS}={DATA_PROV!r}/>"
        outfile += f"{add_indent(indent)}</{ABBR_STR}:DataProvider>"
        return outfile
    outfile += f"</{ABBR_STR}:DataProvider>"
    return outfile


def __write_data_structure(
    data_structure: str, indent: str, references_30: bool = False
) -> str:
    """Writes a DataStructure reference to the XML file."""
    outfile = f"{add_indent(indent)}<{ABBR_STR}:DataStructure>"
    if references_30:
        # SDMX 3.0: URN
        outfile += data_structure
    else:
        # SDMX 2.1: Ref with attributes
        outfile += f"{add_indent(add_indent(indent))}<{REF} "
        ref = parse_urn(data_structure)
        outfile += f"{AGENCY_ID}={ref.agency!r} "
        outfile += f"{ID}={ref.id!r} "
        outfile += f"{VERSION}={ref.version!r} "
        outfile += f"{CLASS}={DSD!r}/>"
        outfile += f"{add_indent(indent)}</{ABBR_STR}:DataStructure>"
        return outfile
    outfile += f"</{ABBR_STR}:DataStructure>"
    return outfile


def __write_dataflow(
    dataflow: str, indent: str, references_30: bool = False
) -> str:
    """Writes a Dataflow reference to the XML file."""
    outfile = f"{add_indent(indent)}<{ABBR_STR}:Dataflow>"
    if references_30:
        # SDMX 3.0: URN
        outfile += dataflow
    else:
        # SDMX 2.1: Ref with attributes
        outfile += f"{add_indent(add_indent(indent))}<{REF} "
        ref = parse_urn(dataflow)
        outfile += f"{AGENCY_ID}={ref.agency!r} "
        outfile += f"{ID}={ref.id!r} "
        outfile += f"{VERSION}={ref.version!r} "
        outfile += f"{CLASS}={DFW!r}/>"
        outfile += f"{add_indent(indent)}</{ABBR_STR}:Dataflow>"
        return outfile
    outfile += f"</{ABBR_STR}:Dataflow>"
    return outfile


def __write_provision_agreement(
    provision_agreement: str, indent: str, references_30: bool = False
) -> str:
    """Writes a ProvisionAgreement reference to the XML file."""
    outfile = f"{add_indent(indent)}<{ABBR_STR}:ProvisionAgreement>"
    if references_30:
        # SDMX 3.0: URN
        outfile += provision_agreement
    else:
        # SDMX 2.1: Ref with attributes
        outfile += f"{add_indent(add_indent(indent))}<{REF} "
        ref = parse_urn(provision_agreement)
        outfile += f"{AGENCY_ID}={ref.agency!r} "
        outfile += f"{ID}={ref.id!r} "
        outfile += f"{VERSION}={ref.version!r}/>"
        outfile += f"{add_indent(indent)}</{ABBR_STR}:ProvisionAgreement>"
        return outfile
    outfile += f"</{ABBR_STR}:ProvisionAgreement>"
    return outfile


def __write_constraint_attachment(
    attachment: ConstraintAttachment, indent: str, references_30: bool = False
) -> str:
    """Writes a ConstraintAttachment to the XML file."""
    outfile = f"{indent}<{ABBR_STR}:{CONS_ATT}>"

    # DataProvider
    if attachment.data_provider:
        outfile += __write_data_provider(
            attachment.data_provider, indent, references_30
        )

    # DataStructures
    if attachment.data_structures:
        for ds in attachment.data_structures:
            outfile += __write_data_structure(ds, indent, references_30)

    # Dataflows
    if attachment.dataflows:
        for df in attachment.dataflows:
            outfile += __write_dataflow(df, indent, references_30)

    # ProvisionAgreements
    if attachment.provision_agreements:
        for pa in attachment.provision_agreements:
            outfile += __write_provision_agreement(pa, indent, references_30)

    outfile += f"{indent}</{ABBR_STR}:{CONS_ATT}>"
    return outfile.replace("'", '"')


def __write_cube_region(
    region: CubeRegion, indent: str, references_30: bool = False
) -> str:
    """Writes a CubeRegion to the XML file."""
    include_val = "true" if region.is_included else "false"

    outfile = f"{indent}<{ABBR_STR}:{CUBE_REGION} {INCLUDE}={include_val!r}>"

    # SDMX 3.0: str, SDMX 2.1: com
    kv_prefix = ABBR_STR if references_30 else ABBR_COM
    val_prefix = ABBR_STR if references_30 else ABBR_COM

    for key_value in region.key_values:
        outfile += f"{add_indent(indent)}"
        outfile += f"<{kv_prefix}:{KEY_VALUE} {ID}={key_value.id!r}>"

        for value in key_value.values:
            value_tag = (
                f"{add_indent(add_indent(indent))}<{val_prefix}:{VALUE}>"
            )
            value_tag += __escape_xml(str(value.value))
            value_tag += f"</{val_prefix}:{VALUE}>"
            outfile += value_tag
        outfile += f"{add_indent(indent)}</{kv_prefix}:{KEY_VALUE}>"

    outfile += f"{indent}</{ABBR_STR}:{CUBE_REGION}>"
    return outfile.replace("'", '"')


def __write_key_set(
    key_set: KeySet, indent: str, references_30: bool = False
) -> str:
    """Writes a DataKeySet to the XML file."""
    include_attr = INCLUDED
    include_val = "true" if key_set.is_included else "false"

    outfile = (
        f"{indent}<{ABBR_STR}:{DATA_KEY_SET} {include_attr}={include_val!r}>"
    )

    # SDMX 3.0: str, SDMX 2.1: com
    kv_prefix = ABBR_STR if references_30 else ABBR_COM
    val_prefix = ABBR_STR if references_30 else ABBR_COM

    for key in key_set.keys:
        outfile += f"{add_indent(indent)}<{ABBR_STR}:{KEY}>"

        for key_value in key.keys_values:
            outfile += f"{add_indent(add_indent(indent))}"
            outfile += f"<{kv_prefix}:{KEY_VALUE} {ID}={key_value.id!r}>"
            value_tag = f"{add_indent(add_indent(add_indent(indent)))}"
            value_tag += f"<{val_prefix}:{VALUE}>"
            value_tag += __escape_xml(str(key_value.value))
            value_tag += f"</{val_prefix}:{VALUE}>"
            outfile += value_tag
            outfile += (
                f"{add_indent(add_indent(indent))}</{kv_prefix}:{KEY_VALUE}>"
            )
        outfile += f"{add_indent(indent)}</{ABBR_STR}:{KEY}>"

    outfile += f"{indent}</{ABBR_STR}:{DATA_KEY_SET}>"
    return outfile.replace("'", '"')


def __write_data_constraint(
    constraint: DataConstraint, indent: str, references_30: bool = False
) -> str:
    """Writes a DataConstraint to the XML file."""
    # SDMX 3.0: DataConstraint, SDMX 2.1: ContentConstraint
    constraint_type = DATA_CONS if references_30 else CON_CONS

    data = __write_maintainable(constraint, indent, references_30)

    # Add role attribute for SDMX 3.0 (required)

    # TODO: add 'role' field to 'DataConstraint'
    # to know which role to use (Allowed | Actual)
    # In SDMX-JSON role is ignored and
    # was deleted from JsonDataConstraint (PR #468)
    if references_30:
        data["Attributes"] += ' role="Allowed"'

    label = f"{ABBR_STR}:{constraint_type}"
    attributes = data.get("Attributes") or ""
    attributes = attributes.replace("'", '"')

    outfile = f"{indent}<{label}{attributes}>"
    outfile += __export_intern_data(data)

    # ConstraintAttachment
    if constraint.constraint_attachment is not None:
        outfile += __write_constraint_attachment(
            constraint.constraint_attachment, add_indent(indent), references_30
        )

    # CubeRegions
    if constraint.cube_regions:
        for region in constraint.cube_regions:
            outfile += __write_cube_region(
                region, add_indent(indent), references_30
            )

    # DataKeySets
    if constraint.key_sets:
        for key_set in constraint.key_sets:
            outfile += __write_key_set(
                key_set, add_indent(indent), references_30
            )

    outfile += f"{indent}</{label}>"
    return outfile


def __write_scheme(  # noqa: C901
    item_scheme: Any, indent: str, scheme: str, references_30: bool = False
) -> str:
    """Writes the scheme to the XML file."""
    if getattr(item_scheme, "sdmx_type", None) == "valuelist":
        scheme = VALUE_LIST

    if scheme == REPRESENTATION_MAP:
        return __write_representation_map(item_scheme, indent, references_30)
    if scheme == STRUCTURE_MAP:
        return __write_structure_map(item_scheme, indent, references_30)
    if isinstance(item_scheme, DataConstraint):
        return __write_data_constraint(item_scheme, indent, references_30)

    label = f"{ABBR_STR}:{scheme}"
    components = ""
    data = __write_maintainable(item_scheme, indent, references_30)

    if scheme == DSD:
        components = __write_components(
            item_scheme, add_indent(indent), references_30
        )

    if scheme not in [DSD, DFW, PROV_AGREEMENT]:
        data["Attributes"] += (
            f" isPartial={str(item_scheme.is_partial).lower()!r}"
        )
    if scheme in [
        RULE_SCHEME,
        UDO_SCHEME,
        TRANS_SCHEME,
        VTL_MAPPING_SCHEME,
        CUSTOM_TYPE_SCHEME,
        NAME_PER_SCHEME,
    ]:
        data["Attributes"] += (
            f" {_write_vtl(item_scheme, indent, references_30)}"
        )

    outfile = ""

    attributes = data.get("Attributes") or ""
    attributes = attributes.replace("'", '"')

    outfile += f"{indent}<{label}{attributes}>"

    outfile += __export_intern_data(data)

    outfile += components

    if scheme == DFW:
        outfile += __write_structure(
            item_scheme.structure, add_indent(indent), references_30
        )
    if scheme == PROV_AGREEMENT:
        outfile += __write_prov_agreement(
            item_scheme.dataflow,
            item_scheme.provider,
            add_indent(indent),
            references_30,
        )

    if scheme not in [
        DSD,
        DFW,
        RULE_SCHEME,
        UDO_SCHEME,
        TRANS_SCHEME,
        VTL_MAPPING_SCHEME,
        CUSTOM_TYPE_SCHEME,
        NAME_PER_SCHEME,
        PROV_AGREEMENT,
    ]:
        for item in item_scheme.items:
            if (
                scheme == AGENCY_SCHEME
                and item.urn is not None
                and references_30
            ):
                agency_id = parse_short_urn(item_scheme.short_urn).agency
                item = copy(
                    item.__replace__(
                        urn=f"urn:sdmx:org.sdmx.infomodel.base.Agency={agency_id}:AGENCIES(1.0).{item.id}"
                    )
                )
            outfile += __write_item(
                item, add_indent(indent), scheme, references_30
            )
    if scheme in [
        RULE_SCHEME,
        UDO_SCHEME,
        TRANS_SCHEME,
        VTL_MAPPING_SCHEME,
        CUSTOM_TYPE_SCHEME,
        NAME_PER_SCHEME,
    ]:
        for item in item_scheme.items:
            outfile += _write_vtl(item, add_indent(indent), references_30)
        outfile += _write_vtl_references(
            item_scheme, add_indent(indent), references_30
        )
    outfile += f"{indent}</{label}>"

    return outfile


def __check_sdmx_type(
    package: Dict[str, Any], key: str, msg_content: Dict[str, Any]
) -> str:
    first_value = next(iter(package[key].values()), None)

    if (
        first_value is not None
        and getattr(first_value, "sdmx_type", None) == VALUE_LIST_LOW
    ):
        return VALUE_LISTS
    else:
        return msg_content[key]


def __write_metadata_element(
    package: Dict[str, Any],
    key: str,
    prettyprint: object,
    references_30: bool = False,
) -> str:
    """Writes the metadata element to the XML file.

    Args:
        package: The package to be written
        key: The key to be used
        prettyprint: Prettyprint or not
        references_30: Whether to use SDMX 3.0 references

    Returns:
        A string with the metadata element
    """
    outfile = ""
    nl = "\n" if prettyprint else ""
    child2 = "\t\t" if prettyprint else ""

    base_indent = f"{nl}{child2}"

    msg_content = MSG_CONTENT_PKG_30 if references_30 else MSG_CONTENT_PKG_21

    if key in package:
        scheme = __check_sdmx_type(package, key, msg_content)
        outfile += f"{base_indent}<{ABBR_STR}:{scheme}>"
        for element in package[key].values():
            item = (
                DSD
                if issubclass(element.__class__, DataStructureDefinition)
                else element.__class__.__name__
            )
            outfile += __write_scheme(
                element, add_indent(base_indent), item, references_30
            )

        outfile += f"{base_indent}</{ABBR_STR}:{scheme}>"

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


def __write_structures(
    content: Dict[str, Any], prettyprint: bool, references_30: bool = False
) -> str:
    """Writes the structures to the XML file.

    Args:
        content: The Message Content to be written
        prettyprint: Prettyprint or not
        references_30: Whether to use SDMX 3.0 references

    Returns:
        A string with the structures
    """
    nl = "\n" if prettyprint else ""
    child1 = "\t" if prettyprint else ""

    outfile = f"{nl}{child1}<{ABBR_MSG}:Structures>"
    msg_content = MSG_CONTENT_PKG_30 if references_30 else MSG_CONTENT_PKG_21
    for key in msg_content:
        outfile += __write_metadata_element(
            content, key, prettyprint, references_30
        )

    outfile += f"{nl}{child1}</{ABBR_MSG}:Structures>"

    # Replace &amp; with & in the outfile
    outfile = outfile.replace("& ", "&amp; ")

    return outfile


def _write_vtl(  # noqa: C901
    item_or_scheme: Union[Item, ItemScheme],
    indent: str,
    references_30: bool = False,
) -> str:  # noqa: C901
    """Writes the VTL attribute to the XML file for a single item.

    This function writes an item or an item scheme to the XML file,
    following the standard format.

    Args:
        item_or_scheme: The item or item scheme to be written
            Item: The item to be written
            ItemScheme: The item scheme to be written
        indent: The current indentation level
        references_30: Whether to use SDMX 3.0 references
    """
    outfile = ""

    if isinstance(item_or_scheme, Item):
        label = ""
        nameable = __write_nameable(item_or_scheme, add_indent(indent))
        attrib = nameable["Attributes"].replace("'", '"')
        data = __export_intern_data(nameable)

        if isinstance(item_or_scheme, Ruleset):
            label = f"{ABBR_STR}:{RULE}"
            data += f"{add_indent(indent)}<{ABBR_STR}:RulesetDefinition>"
            data += (
                f"{__escape_xml(item_or_scheme.ruleset_definition)}"
                f"</{ABBR_STR}:RulesetDefinition>"
            )
            attrib += (
                f" rulesetScope={item_or_scheme.ruleset_scope!r} "
                f"rulesetType={item_or_scheme.ruleset_type!r}"
            )

        if isinstance(item_or_scheme, Transformation):
            label = f"{ABBR_STR}:{TRANSFORMATION}"
            data += f"{add_indent(indent)}<{ABBR_STR}:Expression>"
            data += (
                f"{__escape_xml(item_or_scheme.expression)}"
                f"</{ABBR_STR}:Expression>"
            )
            data += f"{add_indent(indent)}<{ABBR_STR}:Result>"
            data += f"{item_or_scheme.result}</{ABBR_STR}:Result>"
            attrib += (
                f" isPersistent={str(item_or_scheme.is_persistent).lower()!r}"
            )

        if isinstance(item_or_scheme, UserDefinedOperator):
            label = f"{ABBR_STR}:{UDO}"
            data += f"{add_indent(indent)}<{ABBR_STR}:OperatorDefinition>"
            data += (
                f"{__escape_xml(item_or_scheme.operator_definition)}"
                f"</{ABBR_STR}:OperatorDefinition>"
            )
        if isinstance(item_or_scheme, VtlDataflowMapping):
            label = f"{ABBR_STR}:{VTLMAPPING}"
            attrib += f" alias={item_or_scheme.dataflow_alias!r}"
            data += f"{add_indent(indent)}<{ABBR_STR}:Dataflow>"
            reference = item_or_scheme.dataflow
            if references_30:
                data += (
                    f"urn:sdmx:org.sdmx.infomodel.datastructure.{DFW}={reference.agency}:{reference.id}"
                    f"({reference.version})</{ABBR_STR}:Dataflow>"
                )
            else:
                data += (
                    f"{indent}\t\t<{REF} package='datastructure' "
                    f"agencyID={reference.agency!r} id={reference.id!r} "
                    f"version={reference.version!r} class={DFW!r} />"
                    f"{add_indent(indent)}</{ABBR_STR}:Dataflow>"
                )
            if item_or_scheme.to_vtl_mapping_method is not None:
                to_vtl = item_or_scheme.to_vtl_mapping_method
                if len(to_vtl.to_vtl_sub_space) == 0:
                    data += (
                        f"{add_indent(indent)}<{ABBR_STR}:ToVtlMapping "
                        f"method='{to_vtl.method}' />"
                    )
                else:
                    data += (
                        f"{add_indent(indent)}<{ABBR_STR}:ToVtlMapping "
                        f"method='{to_vtl.method}'>"
                    )
                    indent_2 = add_indent(add_indent(indent))
                    data += f"{indent_2}<{ABBR_STR}:ToVtlSubSpace>"
                    for key in to_vtl.to_vtl_sub_space:
                        data += (
                            f"{add_indent(indent_2)}<{ABBR_STR}:Key>{key}"
                            f"</{ABBR_STR}:Key>"
                        )
                    data += f"{indent_2}</{ABBR_STR}:ToVtlSubSpace>"
                    data += f"{add_indent(indent)}</{ABBR_STR}:ToVtlMapping>"

            if item_or_scheme.from_vtl_mapping_method is not None:
                from_vtl = item_or_scheme.from_vtl_mapping_method
                if len(from_vtl.from_vtl_sub_space) == 0:
                    data += (
                        f"{add_indent(indent)}<{ABBR_STR}:FromVtlMapping "
                        f"method={from_vtl.method!r} />"
                        if from_vtl.method is not None
                        else f"method='{from_vtl.method}' />"
                    )
                else:
                    data += (
                        f"{add_indent(indent)}<{ABBR_STR}:FromVtlMapping "
                        f"method='{from_vtl.method}'>"
                    )
                    indent_2 = add_indent(add_indent(indent))
                    data += f"{indent_2}<{ABBR_STR}:FromVtlSuperSpace>"
                    for key in from_vtl.from_vtl_sub_space:
                        data += (
                            f"{add_indent(indent_2)}<{ABBR_STR}:Key>{key}"
                            f"</{ABBR_STR}:Key>"
                        )
                    data += f"{indent_2}</{ABBR_STR}:FromVtlSuperSpace>"
                    data += f"{add_indent(indent)}</{ABBR_STR}:FromVtlMapping>"

        if isinstance(item_or_scheme, VtlCodelistMapping):
            label = f"{ABBR_STR}:{VTLMAPPING}"
            data += f"{add_indent(indent)}<{ABBR_STR}:Codelist>"
            ref_codelist = (
                item_or_scheme.codelist
                if isinstance(item_or_scheme.codelist, Reference)
                else parse_urn(item_or_scheme.codelist)
                if isinstance(item_or_scheme.codelist, str)
                else parse_short_urn(item_or_scheme.codelist.short_urn)
            )
            if references_30:
                data += (
                    f"urn:sdmx:org.sdmx.infomodel.codelist.Codelist={ref_codelist.agency}:{ref_codelist.id}"
                    f"({ref_codelist.version})</{ABBR_STR}:Codelist>"
                )
            else:
                data += (
                    f"{indent}\t\t<{REF} package='codelist' "
                    f"agencyID={ref_codelist.agency!r} id={ref_codelist.id!r} "
                    f"version={ref_codelist.version!r} class={CL!r} />"
                    f"{add_indent(indent)}</{ABBR_STR}:Codelist>"
                )
            attrib += f" alias={item_or_scheme.codelist_alias!r}"

        if isinstance(item_or_scheme, VtlConceptMapping) and not isinstance(
            item_or_scheme.concept, Concept
        ):
            # TODO: Add handling for VtlConceptMapping
            #  when the Concept object is referenced
            label = f"{ABBR_STR}:{VTLMAPPING}"
            data += f"{add_indent(indent)}<{ABBR_STR}:Concept>"
            ref_concept = (
                parse_item_urn(item_or_scheme.concept)
                if isinstance(item_or_scheme.concept, str)
                else item_or_scheme.concept
            )
            if references_30:
                data += (
                    f"urn:sdmx:org.sdmx.infomodel.conceptscheme.Concept={ref_concept.agency}:{ref_concept.id}"
                    f"({ref_concept.version}).{ref_concept.item_id}</{ABBR_STR}:Concept>"
                )
            else:
                data += (
                    f"{indent}\t\t"
                    f"<{REF} maintainableParentID={ref_concept.id!r} "
                    f"package='conceptscheme' "
                    f"agencyID={ref_concept.agency!r} "
                    f"id={ref_concept.item_id!r} "
                    f"maintainableParentVersion={ref_concept.version!r} "
                    f"class={CON!r} />"
                    f"{add_indent(indent)}</{ABBR_STR}:Concept>"
                )
            attrib += f" alias={item_or_scheme.concept_alias!r}"

        if isinstance(item_or_scheme, CustomType):
            label = f"{ABBR_STR}:{CUSTOM_TYPE}"
            data += (
                f"{add_indent(indent)}<{ABBR_STR}:VtlScalarType>"
                f"{item_or_scheme.vtl_scalar_type}"
                f"</{ABBR_STR}:VtlScalarType>"
            )
            data += (
                f"{add_indent(indent)}<{ABBR_STR}:DataType>"
                f"{item_or_scheme.data_type}"
                f"</{ABBR_STR}:DataType>"
            )
            data += (
                (
                    f"{add_indent(indent)}<{ABBR_STR}:VtlLiteralFormat>"
                    f"{item_or_scheme.vtl_literal_format}"
                    f"</{ABBR_STR}:VtlLiteralFormat>"
                )
                if item_or_scheme.vtl_literal_format is not None
                else ""
            )
            data += (
                (
                    f"{add_indent(indent)}<{ABBR_STR}:OutputFormat>"
                    f"{item_or_scheme.output_format}"
                    f"</{ABBR_STR}:OutputFormat>"
                )
                if item_or_scheme.output_format is not None
                else ""
            )
            data += (
                (
                    f"{add_indent(indent)}<{ABBR_STR}:NullValue>"
                    f"{item_or_scheme.null_value}"
                    f"</{ABBR_STR}:NullValue>"
                )
                if item_or_scheme.null_value is not None
                else ""
            )

        if isinstance(item_or_scheme, NamePersonalisation):
            label = f"{ABBR_STR}:{NAME_PER}"
            attrib += f" vtlArtefact={item_or_scheme.vtl_artefact!r} "
            data += (
                f"{add_indent(indent)}<{ABBR_STR}:VtlDefaultName>"
                f"{item_or_scheme.vtl_default_name}"
                f"</{ABBR_STR}:VtlDefaultName>"
            )
            data += (
                f"{add_indent(indent)}<{ABBR_STR}:PersonalisedName>"
                f"{item_or_scheme.personalised_name}"
                f"</{ABBR_STR}:PersonalisedName>"
            )

        outfile += f"{indent}<{label}{attrib}>"
        outfile += data
        outfile += f"{indent}</{label}>"

    if isinstance(item_or_scheme, VtlScheme):
        outfile += f" vtlVersion={item_or_scheme.vtl_version!r}"

    outfile = outfile.replace("'", '"')

    return outfile


def _write_vtl_references(  # noqa: C901
    scheme: ItemScheme, indent: str, references_30: bool = False
) -> str:
    """Writes references to VTL elements to the XML file."""

    def process_references(
        references: Union[Any, Sequence[Any]], element_name: str
    ) -> str:
        """Process the references to VTL elements."""
        outreference = []
        if not isinstance(references, (list, tuple)):
            references = [references]

        for ref in references:
            if isinstance(ref, Reference):
                outreference.append(f"{indent}<{ABBR_STR}:{element_name}>")
                if references_30:
                    outreference.append(
                        f"urn:sdmx:org.sdmx.infomodel.{TRANSFORMATION.lower()}.{element_name}={ref.agency}:{ref.id}"
                        f"({ref.version})</{ABBR_STR}:{element_name}>"
                    )
                else:
                    outreference.append(
                        f"{add_indent(indent)}<{REF} "
                        f"{PACKAGE}={TRANSFORMATION.lower()!r} "
                        f"{AGENCY_ID}={ref.agency!r} "
                        f"{ID}={ref.id!r} "
                        f"{VERSION}={ref.version!r} "
                        f"{CLASS}={ref.sdmx_type!r}/>"
                        f"{indent}</{ABBR_STR}:{element_name}>"
                    )
            if isinstance(ref, ItemScheme):
                ref_to_use = parse_short_urn(ref.short_urn)
                outreference.append(f"{indent}<{ABBR_STR}:{element_name}>")
                if references_30:
                    outreference.append(
                        f"urn:sdmx:org.sdmx.infomodel.{TRANSFORMATION.lower()}.{element_name}={ref_to_use.agency}:"
                        f"{ref_to_use.id}({ref_to_use.version})</{ABBR_STR}:{element_name}>"
                    )
                else:
                    outreference.append(
                        f"{add_indent(indent)}<{REF} "
                        f"{PACKAGE}={TRANSFORMATION.lower()!r} "
                        f"{AGENCY_ID}={ref_to_use.agency!r} "
                        f"{ID}={ref_to_use.id!r} "
                        f"{VERSION}={ref_to_use.version!r} "
                        f"{CLASS}={ref_to_use.sdmx_type!r}/>"
                        f"{indent}</{ABBR_STR}:{element_name}>"
                    )

        return "".join(outreference)

    outfile = ""
    if isinstance(scheme, TransformationScheme):
        outfile += process_references(
            scheme.vtl_mapping_scheme, "VtlMappingScheme"
        )
        outfile += process_references(
            scheme.name_personalisation_scheme, "NamePersonalisationScheme"
        )
        outfile += process_references(
            scheme.custom_type_scheme, "CustomTypeScheme"
        )
        outfile += process_references(scheme.ruleset_schemes, "RulesetScheme")
        outfile += process_references(
            scheme.user_defined_operator_schemes, "UserDefinedOperatorScheme"
        )
    if isinstance(scheme, UserDefinedOperatorScheme):
        outfile += process_references(
            scheme.vtl_mapping_scheme, "VtlMappingScheme"
        )
        outfile += process_references(scheme.ruleset_schemes, "RulesetScheme")
    if isinstance(scheme, RulesetScheme):
        outfile += process_references(
            scheme.vtl_mapping_scheme, "VtlMappingScheme"
        )
    outfile = outfile.replace("'", '"')

    return outfile
