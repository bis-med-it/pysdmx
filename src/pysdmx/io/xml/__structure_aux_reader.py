"""Parsers for reading metadata."""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence, Type, Union

from msgspec import Struct
from msgspec.structs import asdict, replace

from pysdmx.io.xml.__tokens import (
    AGENCIES,
    AGENCY,
    AGENCY_ID,
    AGENCY_SCHEME,
    ALIAS,
    ALIAS_LOW,
    ANNOTATION,
    ANNOTATION_TEXT,
    ANNOTATION_TITLE,
    ANNOTATION_TYPE,
    ANNOTATION_URL,
    ANNOTATIONS,
    AS_STATUS,
    ATT,
    ATT_LIST,
    ATT_LVL,
    ATT_REL,
    ATTACH_GROUP,
    CATEGORISATION,
    CATEGORISATIONS,
    CATEGORY,
    CATEGORY_SCHEME,
    CATEGORY_SCHEMES,
    CL,
    CL_LOW,
    CLASS,
    CLS,
    CODE,
    CODE_ID,
    CODELIST_ALIAS_REF,
    CODES_LOW,
    COMPONENT_MAP,
    COMPONENT_MAPS,
    COMPS,
    CON,
    CON_CONS,
    CON_ID,
    CON_LOW,
    CON_ROLE,
    CON_SCHEMES,
    CONCEPTS,
    CONS_ATT,
    CONSTRAINTS,
    CONTACT,
    CONTEXT_OBJECT,
    CORE_REP,
    CS,
    CUBE_REGION,
    CUSTOM_TYPE,
    CUSTOM_TYPE_SCHEME,
    CUSTOM_TYPE_SCHEMES,
    CUSTOM_TYPES,
    DATA_CONS,
    DATA_CONSTRAINTS,
    DATA_KEY_SET,
    DATA_PROV,
    DATE_PATTERN_MAP,
    DEPARTMENT,
    DESC,
    DFW,
    DFW_ALIAS_LOW,
    DFW_LOW,
    DFWS,
    DIM,
    DIM_LIST,
    DIM_REF,
    DSD,
    DSD_COMPS,
    DSDS,
    DTYPE,
    EMAIL,
    EMAILS,
    ENUM,
    ENUM_FORMAT,
    FACETS,
    FAX,
    FAXES,
    FIXED_VALUE_MAP,
    FIXED_VALUE_MAPS,
    GROUP,
    GROUP_DIM,
    GROUPS_LOW,
    HAS_FORMAL_LEVELS,
    HIERARCHICAL_CODE,
    HIERARCHICAL_CODELIST,
    HIERARCHICAL_CODELISTS,
    HIERARCHIES,
    HIERARCHY,
    HIERARCHY_ASSOCIATION,
    HIERARCHY_ASSOCIATIONS,
    ID,
    INCLUDE,
    INCLUDED,
    INCLUDED_CODELIST,
    IS_EXTERNAL_REF,
    IS_EXTERNAL_REF_LOW,
    IS_FINAL,
    IS_FINAL_LOW,
    IS_PARTIAL,
    IS_PARTIAL_LOW,
    KEY,
    KEY_VALUE,
    LEVEL,
    LEVELED,
    LINK,
    LINKED_HIERARCHY,
    LINKED_OBJECT,
    LOCAL_CODES_LOW,
    LOCAL_DTYPE,
    LOCAL_FACETS_LOW,
    LOCAL_REP,
    MANDATORY,
    MANDATORY_LOW,
    ME_LIST,
    ME_REL,
    MEASURE,
    METADATA,
    MSR,
    NAME,
    NAME_PER,
    NAME_PER_SCHEME,
    NAME_PER_SCHEMES,
    NAME_PERS,
    OBSERVATION,
    ORGS,
    PAR_ID,
    PAR_VER,
    PROV_AGREEMENT,
    PROV_AGREEMENTS,
    REF,
    REPRESENTATION_MAP,
    REPRESENTATION_MAPS,
    REQUIRED,
    ROLE,
    RULE,
    RULE_SCHEME,
    RULE_SCHEMES,
    RULESETS,
    SER_URL,
    SER_URL_LOW,
    SOURCE,
    STR_URL,
    STR_URL_LOW,
    STR_USAGE,
    STRUCTURE,
    STRUCTURE_MAP,
    STRUCTURE_MAPS,
    TARGET,
    TELEPHONE,
    TELEPHONES,
    TEXT,
    TEXT_FORMAT,
    TEXT_TYPE,
    TIME_DIM,
    TITLE,
    TRANS_SCHEME,
    TRANS_SCHEMES,
    TRANSFORMATION,
    TRANSFORMATIONS,
    TYPE,
    UDO,
    UDO_SCHEME,
    UDO_SCHEMES,
    UDOS,
    URI,
    URIS,
    URL,
    URN,
    USAGE,
    VALID_FROM,
    VALID_FROM_LOW,
    VALID_TO,
    VALID_TO_LOW,
    VALUE,
    VALUE_ITEM,
    VALUE_LIST,
    VALUE_LIST_LOW,
    VALUE_LISTS,
    VERSION,
    VTL_CL_MAPP,
    VTL_CON_MAPP,
    VTL_MAPPING_SCHEME,
    VTLMAPPING,
    VTLMAPPING_SCHEMES,
    VTLMAPPINGS,
)
from pysdmx.io.xml.utils import add_list
from pysdmx.model import (
    AgencyScheme,
    Categorisation,
    Category,
    CategoryScheme,
    Code,
    Codelist,
    ComponentMap,
    Concept,
    ConceptScheme,
    ConstraintAttachment,
    CubeKeyValue,
    CubeRegion,
    CubeValue,
    DataConstraint,
    DataKey,
    DataKeyValue,
    DataType,
    DatePatternMap,
    Facets,
    FixedValueMap,
    HierarchicalCode,
    Hierarchy,
    HierarchyAssociation,
    ImplicitComponentMap,
    KeySet,
    LevelType,
    MultiComponentMap,
    MultiRepresentationMap,
    MultiValueMap,
    RepresentationMap,
    StructureMap,
    ValueMap,
    VtlCodelistMapping,
    VtlConceptMapping,
)
from pysdmx.model.__base import (
    Agency,
    Annotation,
    Contact,
    DataflowRef,
    Item,
    ItemReference,
    ItemScheme,
    Reference,
)
from pysdmx.model.dataflow import (
    Component,
    Components,
    Dataflow,
    DataStructureDefinition,
    Group,
    ProvisionAgreement,
    Role,
)
from pysdmx.model.vtl import (
    CustomType,
    CustomTypeScheme,
    FromVtlMapping,
    NamePersonalisation,
    NamePersonalisationScheme,
    Ruleset,
    RulesetScheme,
    ToVtlMapping,
    Transformation,
    TransformationScheme,
    UserDefinedOperator,
    UserDefinedOperatorScheme,
    VtlDataflowMapping,
    VtlMappingScheme,
)
from pysdmx.util import create_full_urn, find_by_urn, is_final, parse_urn

T = Any


def _identity(x: T) -> T:
    return x


def _convert(converter: Callable[[Any], Any], value: Any) -> Any:
    """Applies a converter to a value, or to each item if it is a list."""
    if isinstance(value, list):
        return [converter(v) for v in value]
    return converter(value)


STRUCTURES_MAPPING = {
    CL: Codelist,
    VALUE_LIST: Codelist,
    AGENCY_SCHEME: AgencyScheme,
    CS: ConceptScheme,
    DFWS: Dataflow,
    DSDS: DataStructureDefinition,
    RULE_SCHEME: RulesetScheme,
    UDO_SCHEME: UserDefinedOperatorScheme,
    TRANS_SCHEME: TransformationScheme,
    VTL_MAPPING_SCHEME: VtlMappingScheme,
    STRUCTURE_MAP: StructureMap,
    COMPONENT_MAP: ComponentMap,
    FIXED_VALUE_MAP: FixedValueMap,
    DATE_PATTERN_MAP: DatePatternMap,
    REPRESENTATION_MAP: RepresentationMap,
    NAME_PER_SCHEME: NamePersonalisationScheme,
    CUSTOM_TYPE_SCHEME: CustomTypeScheme,
    PROV_AGREEMENTS: ProvisionAgreement,
    CONSTRAINTS: DataConstraint,
    DATA_CONSTRAINTS: DataConstraint,
    CATEGORY_SCHEME: CategoryScheme,
    CATEGORISATION: Categorisation,
}
ITEMS_CLASSES = {
    AGENCY: Agency,
    CODE: Code,
    VALUE_ITEM: Code,
    CATEGORY: Category,
    CON: Concept,
    RULE: Ruleset,
    UDO: UserDefinedOperator,
    TRANSFORMATION: Transformation,
    VTLMAPPING: VtlDataflowMapping,
    VTL_CL_MAPP: VtlCodelistMapping,
    VTL_CON_MAPP: VtlConceptMapping,
    NAME_PER: NamePersonalisation,
    CUSTOM_TYPE: CustomType,
}

COMP_TYPES = [DIM, ATT, MEASURE, MSR, GROUP_DIM]

ROLE_MAPPING = {
    DIM: Role.DIMENSION,
    ATT: Role.ATTRIBUTE,
    MEASURE: Role.MEASURE,
    MSR: Role.MEASURE,
}

FACETS_MAPPING = {
    "minLength": "min_length",
    "maxLength": "max_length",
    "minValue": "min_value",
    "maxValue": "max_value",
    "startValue": "start_value",
    "endValue": "end_value",
    "interval": "interval",
    "timeInterval": "time_interval",
    "decimals": "decimals",
    "pattern": "pattern",
    "startTime": "start_time",
    "endTime": "end_time",
    "isSequence": "is_sequence",
}


def _extract_text(element: Any) -> str:
    """Extracts the text from the element.

    Args:
        element: The element to extract the text from

    Returns:
        The text extracted from the element
    """
    if isinstance(element, list):
        aux = {}
        for language_element in element:
            if "lang" in language_element and language_element["lang"] == "en":
                aux = language_element
        if not aux:
            aux = element[0]
        element = aux
    if isinstance(element, dict) and "#text" in element:
        element = element["#text"]
    return element


def _format_lower_key(key: str, json_info: Dict[str, Any]) -> None:
    """Formats the key to lower case with underscores and returns it.

    Args:
        key: The key to be formatted
        json_info: The JSON information to be updated

    Returns:
        The formatted key in lower case

    """
    # Replaces the capital letters in the key with lower case,
    # adding an underscore before it if is not the first letter

    if key not in json_info:
        return
    formatted_key = key[0].lower() + "".join(
        "_" + c.lower() if c.isupper() else c for c in key[1:]
    )
    json_info[formatted_key] = json_info.pop(key)


class StructureParser(Struct):
    """StructureParser class for SDMX-ML."""

    agencies: Dict[str, AgencyScheme] = {}
    codelists: Dict[str, Codelist] = {}
    valuelists: Dict[str, Codelist] = {}
    concepts: Dict[str, ConceptScheme] = {}
    datastructures: Dict[str, DataStructureDefinition] = {}
    dataflows: Dict[str, Dataflow] = {}
    constraints: Dict[str, DataConstraint] = {}
    rulesets: Dict[str, RulesetScheme] = {}
    udos: Dict[str, UserDefinedOperatorScheme] = {}
    vtl_mappings: Dict[str, VtlMappingScheme] = {}
    structure_maps: Dict[str, StructureMap] = {}
    component_maps: Dict[str, ComponentMap] = {}
    fixed_value_maps: Dict[str, FixedValueMap] = {}
    representation_maps: Dict[
        str, Union[RepresentationMap, MultiRepresentationMap]
    ] = {}
    name_personalisations: Dict[str, NamePersonalisationScheme] = {}
    custom_types: Dict[str, CustomTypeScheme] = {}
    transformations: Dict[str, TransformationScheme] = {}
    category_schemes: Dict[str, CategoryScheme] = {}
    categorisations: Dict[str, Categorisation] = {}
    is_sdmx_30: bool = False

    def __format_contact(self, json_contact: Dict[str, Any]) -> Contact:
        """Creates a Contact object from a json_contact.

        Args:
            json_contact: The element to create the Contact object from

        Returns:
            Contact object created from the json_contact
        """
        self.__format_name_description(json_contact)

        xml_node_to_attribute = {
            NAME: NAME.lower(),
            DEPARTMENT: DEPARTMENT.lower(),
            ROLE: ROLE.lower(),
            URI: URIS,
            EMAIL: EMAILS,
            TELEPHONE: TELEPHONES,
            FAX: FAXES,
        }

        for k, v in xml_node_to_attribute.items():
            if k in json_contact:
                if k in [DEPARTMENT, ROLE]:
                    json_contact[v] = _extract_text(json_contact.pop(k))
                    continue
                field_info = add_list(json_contact.pop(k))
                for i, element in enumerate(field_info):
                    field_info[i] = _extract_text(element)
                json_contact[v] = field_info

        return Contact(**json_contact)

    @staticmethod
    def __format_annotations(item_elem: Any) -> Dict[str, Any]:
        """Formats the annotations in this element.

        Args:
            item_elem: The element to be formatted

        Returns:
            annotations formatted
        """
        if LINK in item_elem:
            del item_elem[LINK]
        if ANNOTATIONS not in item_elem:
            return item_elem
        annotations = []

        ann = item_elem[ANNOTATIONS]
        ann[ANNOTATION] = add_list(ann[ANNOTATION])
        for e in ann[ANNOTATION]:
            if ANNOTATION_TITLE in e:
                e[TITLE] = e.pop(ANNOTATION_TITLE)
            if ANNOTATION_TYPE in e:
                e[TYPE] = e.pop(ANNOTATION_TYPE)
            if ANNOTATION_TEXT in e:
                e[TEXT] = _extract_text(e[ANNOTATION_TEXT])
                del e[ANNOTATION_TEXT]
            if ANNOTATION_URL in e:
                e[URL] = e.pop(ANNOTATION_URL)

            annotations.append(Annotation(**e))

        item_elem[ANNOTATIONS.lower()] = annotations
        del item_elem[ANNOTATIONS]

        return item_elem

    @staticmethod
    def __format_name_description(element: Any) -> Dict[str, Any]:
        node = [NAME, DESC]
        for field in node:
            if field in element:
                element[field.lower()] = _extract_text(element[field])
                del element[field]
        return element

    @staticmethod
    def __format_facets(
        json_fac: Dict[str, Any], json_obj: Dict[str, Any]
    ) -> None:
        """Formats the facets from the JSON information.

        Args:
            json_fac: The element with the facets to be formatted
            json_obj: The element to store the formatted facets
        """
        if json_fac is None:
            return
        for key in json_fac:
            if key == TEXT_TYPE and json_fac[TEXT_TYPE] in list(DataType):
                json_obj["dtype"] = DataType(json_fac[TEXT_TYPE])

            if key in FACETS_MAPPING:
                facet_kwargs = {
                    FACETS_MAPPING[k]: v
                    for k, v in json_fac.items()
                    if k in FACETS_MAPPING
                }
                json_obj[FACETS.lower()] = Facets(**facet_kwargs)

    @staticmethod
    def __format_validity(element: Dict[str, Any]) -> Dict[str, Any]:
        if VALID_FROM in element:
            element[VALID_FROM_LOW] = datetime.fromisoformat(
                element.pop(VALID_FROM)
            )
        if VALID_TO in element:
            element[VALID_TO_LOW] = datetime.fromisoformat(
                element.pop(VALID_TO)
            )
        return element

    @staticmethod
    def __format_urls(json_elem: Dict[str, Any]) -> Dict[str, Any]:
        """Formats the STR_URL and SER_URL keys in the element.

        Args:
            json_elem: The element to be formatted

        Returns:
            The json_elem with STR_URL and SER_URL keys formatted.
        """
        if STR_URL in json_elem:
            json_elem[STR_URL_LOW] = json_elem.pop(STR_URL)
        if SER_URL in json_elem:
            json_elem[SER_URL_LOW] = json_elem.pop(SER_URL)
        return json_elem

    def __format_agency(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Formats the AGENCY_ID key in the element to the maintainer.

        Args:
            element: The element with the Agency ID to be formatted

        Returns:
            element with the Agency ID formatted
        """
        element[AGENCY.lower()] = self.agencies.get(
            element[AGENCY_ID], element[AGENCY_ID]
        )
        del element[AGENCY_ID]
        return element

    def __format_orgs(self, json_orgs: Dict[str, Any]) -> Dict[str, Any]:
        orgs: Dict[str, Any] = {}
        json_list = add_list(json_orgs)
        for e in json_list:
            self.__strip_agency_scheme_defaults(e)
            ag_sch = self.__format_scheme(
                e,
                AGENCY_SCHEME,
                AGENCY,
            )
            orgs = {**orgs, **ag_sch}
        return orgs

    @staticmethod
    def __strip_agency_scheme_defaults(
        element: Dict[str, Any],
    ) -> None:
        """Remove default AgencyScheme fields before construction.

        The SDMX standard defines fixed values for AgencyScheme id,
        name, and version. Stripping them when they match the defaults
        aligns the XML reader with the JSON reader behavior.
        """
        for s in add_list(element[AGENCY_SCHEME]):
            for k, v in [("id", "AGENCIES"), ("version", "1.0")]:
                if s.get(k) == v:
                    del s[k]
            name = s.get(NAME)
            if name is not None and _extract_text(name) == "AGENCIES":
                del s[NAME]

    def __format_representation(
        self, json_rep: Dict[str, Any], json_obj: Dict[str, Any]
    ) -> None:
        """Formats the representation in the JSON Representation."""
        if TEXT_FORMAT in json_rep:
            self.__format_facets(json_rep[TEXT_FORMAT], json_obj)

        if ENUM in json_rep and (
            len(self.codelists) > 0 or len(self.valuelists) > 0
        ):
            enum = json_rep[ENUM]
            if isinstance(enum, str):
                ref = parse_urn(enum)
            else:
                ref = enum.get(REF, enum)
            if isinstance(ref, dict) and "URN" in ref:
                codelist = find_by_urn(
                    list(self.codelists.values()), ref["URN"]
                )

            elif isinstance(ref, Reference):
                codelist = find_by_urn(
                    list(
                        self.codelists.values()
                        if ref.sdmx_type == CL
                        else self.valuelists.values()
                    ),
                    str(ref),
                )
            else:
                short_urn = str(
                    Reference(
                        sdmx_type=ref[CLASS],  # type: ignore[index]
                        agency=ref[AGENCY_ID],  # type: ignore[index]
                        id=ref[ID],  # type: ignore[index]
                        version=ref[VERSION],  # type: ignore[index]
                    )
                )
                codelist = self.codelists[short_urn]

            json_obj[CODES_LOW] = codelist
        if ENUM_FORMAT in json_rep:
            self.__format_facets(json_rep[ENUM_FORMAT], json_obj)

    def __format_local_rep(self, representation_info: Dict[str, Any]) -> None:
        rep: Dict[str, Any] = {}

        self.__format_representation(representation_info[LOCAL_REP], rep)
        del representation_info[LOCAL_REP]

        if CODES_LOW in rep:
            representation_info[LOCAL_CODES_LOW] = rep.pop(CODES_LOW)

        if DTYPE in rep:
            representation_info[LOCAL_DTYPE] = rep.pop(DTYPE)

        if FACETS.lower() in rep:
            representation_info[LOCAL_FACETS_LOW] = rep.pop(FACETS.lower())

    def __format_con_id(
        self, concept_ref: Union[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        if isinstance(concept_ref, str):
            item_reference = parse_urn(concept_ref)
        else:
            item_reference = ItemReference(
                sdmx_type=concept_ref[CLASS],
                agency=concept_ref[AGENCY_ID],
                id=concept_ref[PAR_ID],
                version=concept_ref[PAR_VER],
                item_id=concept_ref[ID],
            )
        scheme_reference = Reference(
            sdmx_type=CS,
            agency=item_reference.agency,
            id=item_reference.id,
            version=item_reference.version,
        )

        concept_scheme = self.concepts.get(str(scheme_reference))

        if concept_scheme is None:
            return {CON: item_reference}

        short_urn = str(item_reference)
        for con in concept_scheme.concepts:
            con_short = str(
                ItemReference(
                    sdmx_type=item_reference.sdmx_type,
                    agency=item_reference.agency,
                    id=item_reference.id,
                    version=item_reference.version,
                    item_id=con.id,
                )
            )

            if con_short == short_urn:
                if con.urn is None:
                    con = Concept(
                        **{
                            **asdict(con),
                            "urn": (
                                "urn:sdmx:org.sdmx.infomodel.conceptscheme."
                                f"{short_urn}"
                            ),
                        }
                    )
                return {CON: con}

        return {CON: item_reference}

    @staticmethod
    def __get_attachment_level(  # noqa: C901
        attribute: Dict[str, Any], element_info: Dict[str, Any]
    ) -> str:
        if DIM in attribute:
            dims = add_list(attribute[DIM])
            if dims and isinstance(dims[0], dict):
                dims = [dim[REF][ID] for dim in dims]
            att_level = ",".join(dims)
            # AttachmentGroup can only appear as sequence of the Dimension,
            # therefore we need to check first if a Dimension is present,
            # then the AttachmentGroup
            if ATTACH_GROUP in attribute:
                att_grp = add_list(attribute[ATTACH_GROUP])
                att_grp = [att[REF][ID] for att in att_grp]
                for grp in att_grp:
                    group_dims: List[str] = next(
                        (
                            g.dimensions
                            for g in element_info[GROUPS_LOW]
                            if g.id == grp
                        ),
                        [],
                    )
                    att_level += (
                        "," + ",".join(group_dims)
                        if len(group_dims) > 0
                        else ""
                    )
        elif GROUP in attribute:
            if isinstance(attribute[GROUP], dict) and REF in attribute[GROUP]:
                group_id = attribute[GROUP][REF][ID]
            else:
                group_id = attribute[GROUP]
            group_dimensions: List[str] = next(
                (
                    g.dimensions
                    for g in element_info[GROUPS_LOW]
                    if g.id == group_id
                ),
                [],
            )
            att_level = (
                ",".join(group_dimensions) if len(group_dimensions) > 0 else ""
            )
        elif OBSERVATION in attribute or MEASURE in attribute:
            att_level = "O"
        else:
            # For None (SDMX-2.1) or Dataflow (SDMX-3.0), attribute is
            # related to Dataset/Dataflow
            att_level = "D"

        return att_level

    def __format_vtl_references(
        self, json_elem: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Formats the references in the VTL element."""

        def extract_references(
            scheme: str,
            new_key: str,
            object_list: Dict[str, Any],
            as_list: bool = True,
        ) -> None:
            references = []
            if scheme in json_elem:
                scheme_entries = (
                    json_elem[scheme]
                    if isinstance(json_elem[scheme], list)
                    else [json_elem[scheme]]
                )
                for entry in scheme_entries:
                    if isinstance(entry, str):
                        entry_ref = parse_urn(entry)
                        ref_id = entry_ref.id
                        reference = entry_ref
                    else:
                        ref = entry[REF]
                        ref_id = ref[ID]
                        reference = Reference(
                            sdmx_type=ref[CLASS],
                            agency=ref[AGENCY_ID],
                            id=ref_id,
                            version=ref[VERSION],
                        )

                    matching_object = next(
                        (
                            obj
                            for obj in object_list.values()
                            if getattr(obj, ID, None) == ref_id
                        ),
                        None,
                    )

                    if matching_object:
                        references.append(matching_object)
                    else:
                        references.append(reference)

                if not as_list:
                    json_elem[new_key] = references[0]
                else:
                    json_elem[new_key] = references
                json_elem.pop(scheme)

        extract_references(RULE_SCHEME, "ruleset_schemes", self.rulesets)
        extract_references(
            UDO_SCHEME, "user_defined_operator_schemes", self.udos
        )
        extract_references(
            VTL_MAPPING_SCHEME,
            "vtl_mapping_scheme",
            self.vtl_mappings,
            as_list=False,
        )
        extract_references(
            NAME_PER_SCHEME,
            "name_personalisation_scheme",
            self.name_personalisations,
            as_list=False,
        )
        extract_references(
            CUSTOM_TYPE_SCHEME,
            "custom_type_scheme",
            self.custom_types,
            as_list=False,
        )
        return json_elem

    def __format_dataflow(
        self,
        json_rep: Union[str, Dict[str, Any]],
        json_obj: Dict[str, Any],
    ) -> None:
        json_obj[DFW_ALIAS_LOW] = json_obj.pop(ALIAS_LOW)
        if isinstance(json_rep, str):
            ref_aux = parse_urn(json_rep)
            dataflow_ref = {
                "agency": ref_aux.agency,
                "id": ref_aux.id,
                "version": ref_aux.version,
            }
        else:
            dataflow_ref = {
                "agency": json_rep[REF][AGENCY_ID],
                "id": json_rep[REF][ID],
                "version": json_rep[REF][VERSION],
            }
        json_obj[DFW_LOW] = DataflowRef(**dataflow_ref)
        if isinstance(json_rep, dict) and REF in json_rep:
            json_rep.pop(REF)
        json_obj.pop(DFW)
        if self.dataflows:
            for dataflow in self.dataflows.values():
                if dataflow.id == dataflow_ref[ID]:
                    json_obj[DFW_LOW] = dataflow

    def __format_component(
        self, comp: Dict[str, Any], role: Role, element_info: Dict[str, Any]
    ) -> Component:
        comp[ROLE.lower()] = role
        comp[REQUIRED] = True

        self.__format_local_rep(comp) if LOCAL_REP in comp else None

        if LINK in comp:
            del comp[LINK]
        if isinstance(comp[CON_ID], dict) and REF in comp[CON_ID]:
            concept_id = self.__format_con_id(comp[CON_ID][REF])
        else:
            concept_id = self.__format_con_id(comp[CON_ID])
        comp[CON_LOW] = concept_id.pop(CON)
        del comp[CON_ID]

        # Attribute Handling
        if ATT_REL in comp:
            comp[ATT_LVL] = self.__get_attachment_level(
                comp[ATT_REL], element_info
            )
            del comp[ATT_REL]

        if ME_REL in comp:
            measures = add_list(comp[ME_REL][MSR])
            if len(measures) == 1 and measures[0] == "OBS_VALUE":
                comp[ATT_LVL] = "O"
            else:
                comp[ATT_LVL] = ",".join(measures)
            del comp[ME_REL]

        if AS_STATUS in comp or USAGE in comp:
            status_key = AS_STATUS if AS_STATUS in comp else USAGE
            if (
                comp[status_key] != MANDATORY
                and comp[status_key] != MANDATORY_LOW
            ):
                comp[REQUIRED] = False
            del comp[status_key]

        unwanted_keys = ["position", ANNOTATIONS, CON_ROLE]
        for key in unwanted_keys:
            if key in comp:
                del comp[key]

        return Component(**comp)

    def __format_component_lists(
        self, element: Dict[str, Any], element_info: Dict[str, Any]
    ) -> List[Component]:
        comp_list = []

        if TIME_DIM in element:
            element[DIM] = add_list(element[DIM])
            element[DIM].append(element[TIME_DIM])
            del element[TIME_DIM]

        role_name = list(set(element.keys()).intersection(COMP_TYPES))[0]
        role = ROLE_MAPPING[role_name]
        element[role_name] = add_list(element[role_name])

        for comp in element[role_name]:
            formatted_comp = self.__format_component(
                comp,
                role,
                element_info,
            )
            comp_list.append(formatted_comp)

        return comp_list

    def __format_components(self, element: Dict[str, Any]) -> Dict[str, Any]:
        if DSD_COMPS in element:
            element[COMPS] = []
            comps = element[DSD_COMPS]

            for comp_list in [DIM_LIST, ME_LIST, ATT_LIST]:
                if comp_list in comps:
                    fmt_comps = self.__format_component_lists(
                        comps[comp_list], element
                    )
                    element[COMPS].extend(fmt_comps)

            element[COMPS] = Components(element[COMPS])
            del element[DSD_COMPS]

        return element

    def __format_prov_agreement(
        self, element: Dict[str, Any]
    ) -> Dict[str, Any]:
        dfw = None
        if STR_USAGE in element:
            ref_dfw: Union[Reference, ItemReference]
            if REF in element[STR_USAGE]:
                str_usage = element[STR_USAGE][REF]
                ref_dfw = Reference(
                    sdmx_type=str_usage[CLASS],
                    agency=str_usage[AGENCY_ID],
                    id=str_usage[ID],
                    version=str_usage[VERSION],
                )
            else:
                ref_dfw = parse_urn(element[STR_USAGE][URN])
            dfw = (
                f"{ref_dfw.sdmx_type}={ref_dfw.agency}:"
                f"{ref_dfw.id}({ref_dfw.version})"
            )
            del element[STR_USAGE]

        if DFW in element:
            ref_dfw = parse_urn(element[DFW])
            dfw = (
                f"{ref_dfw.sdmx_type}={ref_dfw.agency}:"
                f"{ref_dfw.id}({ref_dfw.version})"
            )
            del element[DFW]

        ref_data_prov: Union[Reference, ItemReference]
        if isinstance(element[DATA_PROV], dict) and REF in element[DATA_PROV]:
            data_prov = element[DATA_PROV][REF]
            ref_data_prov = ItemReference(
                sdmx_type=data_prov[CLASS],
                agency=data_prov[AGENCY_ID],
                id=data_prov[PAR_ID],
                version=data_prov[PAR_VER],
                item_id=data_prov[ID],
            )
        elif URN in element[DATA_PROV]:
            ref_data_prov = parse_urn(element[DATA_PROV][URN])
        else:
            ref_data_prov = parse_urn(element[DATA_PROV])
        del element[DATA_PROV]
        provider = (
            f"{ref_data_prov.sdmx_type}={ref_data_prov.agency}:"
            f"{ref_data_prov.id}({ref_data_prov.version})"
            f".{ref_data_prov.item_id}"  # type: ignore[union-attr]
        )

        element["dataflow"] = dfw
        element["provider"] = provider

        return element

    def __parse_data_provider(
        self, attachment: Dict[str, Any]
    ) -> Optional[str]:
        if DATA_PROV not in attachment:
            return None
        dp_elem = attachment[DATA_PROV]
        if isinstance(dp_elem, str):
            # SDMX 3.0 format (direct URN)
            return dp_elem
        # SDMX 2.1 format (Ref element)
        ref = dp_elem[REF]
        ref_data_prov = ItemReference(
            sdmx_type=ref[CLASS],
            agency=ref[AGENCY_ID],
            id=ref[PAR_ID],
            version=ref[PAR_VER],
            item_id=ref[ID],
        )
        return (
            f"{ref_data_prov.sdmx_type}={ref_data_prov.agency}:"
            f"{ref_data_prov.id}({ref_data_prov.version})"
            f".{ref_data_prov.item_id}"
        )

    def __parse_references(
        self, attachment: Dict[str, Any], key: str, sdmx_type: str
    ) -> List[str]:
        """Extracts and converts references to URNs."""
        if key not in attachment:
            return []
        ref_list = add_list(attachment[key])

        urns = []
        for ref_elem in ref_list:
            if isinstance(ref_elem, str):
                # SDMX 3.0 format (direct URN)
                urns.append(ref_elem)
            else:
                # SDMX 2.1 format
                ref = ref_elem[REF]
                urn = (
                    f"urn:sdmx:org.sdmx.infomodel.{sdmx_type}="
                    f"{ref[AGENCY_ID]}:{ref[ID]}({ref[VERSION]})"
                )
                urns.append(urn)
        return urns

    def __format_constraint_attachment(
        self, attachment: Dict[str, Any]
    ) -> ConstraintAttachment:
        data_provider = self.__parse_data_provider(attachment)
        dataflows = self.__parse_references(
            attachment, DFW, "datastructure.Dataflow"
        )
        data_structures = self.__parse_references(
            attachment, DSD, "datastructure.DataStructure"
        )
        provision_agreements = self.__parse_references(
            attachment, PROV_AGREEMENT, "registry.ProvisionAgreement"
        )

        return ConstraintAttachment(
            data_provider=data_provider,
            data_structures=data_structures or None,
            dataflows=dataflows or None,
            provision_agreements=(provision_agreements or None),
        )

    def __format_cube_region(self, region_elem: Dict[str, Any]) -> CubeRegion:
        if region_elem is None:
            return CubeRegion(key_values=[], is_included=True)
        is_included = True
        if INCLUDE in region_elem:
            is_included = region_elem[INCLUDE].lower() == "true"

        key_values = []
        if KEY_VALUE in region_elem:
            kv_list = add_list(region_elem[KEY_VALUE])
            for kv in kv_list:
                values = []
                value_list = add_list(kv[VALUE])
                for v in value_list:
                    value_text = v if isinstance(v, str) else v.get("#text", v)
                    values.append(CubeValue(value=value_text))

                key_values.append(CubeKeyValue(id=kv[ID], values=values))

        return CubeRegion(key_values=key_values, is_included=is_included)

    def __format_key_set(self, keyset_elem: Dict[str, Any]) -> KeySet:
        is_included = keyset_elem[INCLUDED].lower() == "true"

        keys = []
        key_list = add_list(keyset_elem[KEY])
        for k in key_list:
            if k is None:
                keys.append(DataKey(keys_values=[]))
                continue
            keys_values = []
            if KEY_VALUE in k:
                kv_list = add_list(k[KEY_VALUE])
                for kv in kv_list:
                    v = kv[VALUE]
                    value_text = v if isinstance(v, str) else v.get("#text", v)

                    keys_values.append(
                        DataKeyValue(id=kv[ID], value=value_text)
                    )

            keys.append(DataKey(keys_values=keys_values))

        return KeySet(keys=keys, is_included=is_included)

    def __format_constraint(self, element: Dict[str, Any]) -> Dict[str, Any]:
        # role is a SDMX 3.0 attribute not present in the model
        if "role" in element:
            if element["role"] == "Actual":
                raise NotImplementedError(
                    "DataConstraint with role='Actual' is not supported, "
                    "pysdmx only supports maintainable (Allowed) constraints."
                )
            del element["role"]

        # ConstraintAttachment
        constraint_attachment = None
        if CONS_ATT in element:
            constraint_attachment = self.__format_constraint_attachment(
                element[CONS_ATT]
            )
            del element[CONS_ATT]

        # CubeRegions
        cube_regions: List[CubeRegion] = []
        if CUBE_REGION in element:
            region_list = add_list(element[CUBE_REGION])
            cube_regions.extend(
                self.__format_cube_region(region) for region in region_list
            )
            del element[CUBE_REGION]

        # KeySets
        key_sets: List[KeySet] = []
        if DATA_KEY_SET in element:
            keyset_list = add_list(element[DATA_KEY_SET])
            key_sets.extend(
                self.__format_key_set(keyset) for keyset in keyset_list
            )
            del element[DATA_KEY_SET]

        element["constraint_attachment"] = constraint_attachment
        element["cube_regions"] = cube_regions
        element["key_sets"] = key_sets

        return element

    def __format_vtl(self, json_vtl: Dict[str, Any]) -> Dict[str, Any]:
        # VTL Scheme Handling
        _format_lower_key("vtlVersion", json_vtl)
        # Transformation Scheme Handling
        if "isPersistent" in json_vtl:
            json_vtl["is_persistent"] = (
                json_vtl.pop("isPersistent").lower() == "true"
            )
        _format_lower_key("Expression", json_vtl)
        _format_lower_key("Result", json_vtl)

        # Ruleset Handling
        _format_lower_key("rulesetScope", json_vtl)
        _format_lower_key("rulesetType", json_vtl)
        _format_lower_key("RulesetDefinition", json_vtl)
        # User Defined Operator Handling
        _format_lower_key("OperatorDefinition", json_vtl)
        # Dataflow Mapping
        if "ToVtlMapping" in json_vtl:
            to_vtl = json_vtl.pop("ToVtlMapping")
            if "ToVtlSubSpace" in to_vtl:
                to_vtl["to_vtl_sub_space"] = add_list(
                    to_vtl["ToVtlSubSpace"]["Key"]
                )
                del to_vtl["ToVtlSubSpace"]
            json_vtl["to_vtl_mapping_method"] = ToVtlMapping(**to_vtl)
        if "FromVtlMapping" in json_vtl:
            from_vtl = json_vtl.pop("FromVtlMapping")
            if "FromVtlSuperSpace" in from_vtl:
                from_vtl["from_vtl_sub_space"] = add_list(
                    from_vtl["FromVtlSuperSpace"]["Key"]
                )
                del from_vtl["FromVtlSuperSpace"]
            json_vtl["from_vtl_mapping_method"] = FromVtlMapping(**from_vtl)
        # Codelist Mapping
        if CL in json_vtl:
            if isinstance(json_vtl[CL], str):
                cl_ref_aux = parse_urn(json_vtl[CL])
                ref = Reference(
                    sdmx_type=CL,
                    agency=cl_ref_aux.agency,
                    id=cl_ref_aux.id,
                    version=cl_ref_aux.version,
                )
            else:
                cl_ref = json_vtl[CL][REF]
                ref = Reference(
                    sdmx_type=CL,
                    agency=cl_ref[AGENCY_ID],
                    id=cl_ref[ID],
                    version=cl_ref[VERSION],
                )
            json_vtl[CL_LOW] = self.codelists.get(str(ref), ref)
            del json_vtl[CL]
            json_vtl["codelist_alias"] = json_vtl.pop("alias")
        # Concept mapping
        if CON in json_vtl:
            if isinstance(json_vtl[CON], str):
                con_ref_aux = parse_urn(json_vtl[CON])
                item_ref = ItemReference(
                    sdmx_type=CON,
                    agency=con_ref_aux.agency,
                    id=con_ref_aux.id,
                    version=con_ref_aux.version,
                    item_id=con_ref_aux.item_id,  # type: ignore[union-attr]
                )
            else:
                con_ref = json_vtl[CON][REF]
                item_ref = ItemReference(
                    sdmx_type=CON,
                    agency=con_ref[AGENCY_ID],
                    id=con_ref[PAR_ID],
                    version=con_ref[PAR_VER],
                    item_id=con_ref[ID],
                )
            json_vtl[CON_LOW] = self.concepts.get(str(item_ref), item_ref)
            del json_vtl[CON]
            json_vtl["concept_alias"] = json_vtl.pop("alias")
        # Custom type
        _format_lower_key("VtlScalarType", json_vtl)
        _format_lower_key("DataType", json_vtl)
        _format_lower_key("NullValue", json_vtl)
        _format_lower_key("OutputFormat", json_vtl)
        _format_lower_key("VtlLiteralFormat", json_vtl)

        # Name Personalisation
        _format_lower_key("PersonalisedName", json_vtl)
        _format_lower_key("vtlArtefact", json_vtl)
        _format_lower_key("VtlDefaultName", json_vtl)

        return json_vtl

    def __format_item(
        self, item_json_info: Dict[str, Any], item_name_class: str
    ) -> Item:
        item_json_info = self.__format_annotations(item_json_info)
        item_json_info = self.__format_name_description(item_json_info)
        if CONTACT in item_json_info and item_name_class == AGENCY:
            item_json_info[CONTACT] = add_list(item_json_info[CONTACT])
            contacts = [
                self.__format_contact(e) for e in item_json_info[CONTACT]
            ]
            item_json_info[CONTACT.lower() + "s"] = contacts
            del item_json_info[CONTACT]

        if CORE_REP in item_json_info and item_name_class == CON:
            self.__format_representation(
                item_json_info[CORE_REP], item_json_info
            )
            del item_json_info[CORE_REP]

        if "Parent" in item_json_info:
            del item_json_info["Parent"]
        if DFW in item_json_info:
            self.__format_dataflow(item_json_info[DFW], item_json_info)

        item_json_info = self.__format_vtl(item_json_info)

        if CL_LOW in item_json_info and item_name_class == VTLMAPPING:
            item_name_class = VTL_CL_MAPP
        elif CON_LOW in item_json_info and item_name_class == VTLMAPPING:
            item_name_class = VTL_CON_MAPP

        return ITEMS_CLASSES[item_name_class](**item_json_info)

    @staticmethod
    def __format_groups(element: Dict[str, Any]) -> Dict[str, Any]:
        if DSD_COMPS in element:
            dsd_comps = element[DSD_COMPS]
            if GROUP in dsd_comps:
                groups = (
                    dsd_comps[GROUP]
                    if isinstance(dsd_comps[GROUP], list)
                    else [dsd_comps[GROUP]]
                )
                for group in groups:
                    group_dimensions = group.pop(GROUP_DIM, [])
                    if isinstance(group_dimensions, dict):
                        group_dimensions = [group_dimensions]

                    group["dimensions"] = [
                        (
                            d[DIM_REF]
                            if isinstance(d[DIM_REF], str)
                            else d[DIM_REF][REF][ID]
                        )
                        for d in group_dimensions
                    ]

                element[GROUPS_LOW] = [Group(**g) for g in groups]
                del element[DSD_COMPS][GROUP]
        return element

    def __build_component_map(
        self, child_dict: Dict[str, Any]
    ) -> Union[ComponentMap, MultiComponentMap, ImplicitComponentMap]:
        if "values" not in child_dict:
            return ImplicitComponentMap(
                source=child_dict["source"],
                target=child_dict["target"],
            )

        src_list = add_list(child_dict.get("source"))
        tgt_list = add_list(child_dict.get("target"))

        if len(src_list) != 1 or len(tgt_list) != 1:
            return MultiComponentMap(
                source=src_list,
                target=tgt_list,
                values=child_dict["values"],
            )

        return ComponentMap(
            source=src_list[0],
            target=tgt_list[0],
            values=child_dict["values"],
        )

    def __build_representation_map(
        self, structure: Dict[str, Any]
    ) -> Union[RepresentationMap, MultiRepresentationMap]:
        src_list = add_list(structure.get("source"))
        tgt_list = add_list(structure.get("target"))

        if len(src_list) != 1 or len(tgt_list) != 1:
            structure["source"] = src_list
            structure["target"] = tgt_list
            return MultiRepresentationMap(**structure)

        structure["source"] = src_list[0]
        structure["target"] = tgt_list[0]
        return RepresentationMap(**structure)

    def __build_representation_mapping(
        self, child_dict: Dict[str, Any]
    ) -> Union[ValueMap, MultiValueMap]:
        src = child_dict.get("source")
        tgt = child_dict.get("target")

        src_list = add_list(src) if src is not None else []
        tgt_list = add_list(tgt) if tgt is not None else []

        if len(src_list) != 1 or len(tgt_list) != 1:
            return MultiValueMap(
                source=src_list,
                target=tgt_list,
                valid_from=child_dict.get("valid_from"),
                valid_to=child_dict.get("valid_to"),
            )

        return ValueMap(
            source=src_list[0],
            target=tgt_list[0],
            valid_from=child_dict.get("valid_from"),
            valid_to=child_dict.get("valid_to"),
        )

    def __format_maps(self, element: Dict[str, Any]) -> Dict[str, Any]:
        if "sourcePattern" in element:
            element["pattern_type"] = (
                # DatePatternMap.pattern_type defaults value is fixed
                "variable" if "FrequencyDimension" in element else "fixed"
            )

        renames = {
            "Source": "source",
            "Target": "target",
            "Value": "value",
            "SourceCodelist": "source",
            "SourceDataType": "source",
            "TargetCodelist": "target",
            "TargetDataType": "target",
            "SourceValue": "source",
            "TargetValue": "target",
            "RepresentationMap": "values",
            "sourcePattern": "pattern",
            "resolvePeriod": "resolve_period",
            "TargetFrequencyID": "frequency",
            "FrequencyDimension": "frequency",
            "validFrom": "valid_from",
            "validTo": "valid_to",
        }
        converters: Dict[str, Callable[[Any], Any]] = {
            "SourceDataType": DataType,
            "TargetDataType": DataType,
        }

        for xml_key, py_key in renames.items():
            if xml_key in element:
                value = element.pop(xml_key)
                element[py_key] = _convert(
                    converters.get(xml_key, _identity), value
                )

        child_class_mapping: Dict[str, Type[Any]] = {
            "ComponentMap": ComponentMap,
            "FixedValueMap": FixedValueMap,
            "DatePatternMap": DatePatternMap,
            "RepresentationMapping": ValueMap,
        }

        MapChild = Union[
            ComponentMap,
            MultiComponentMap,
            ImplicitComponentMap,
            FixedValueMap,
            DatePatternMap,
            ValueMap,
            MultiValueMap,
        ]
        consolidated_children: List[MapChild] = []

        for xml_tag, target_class in child_class_mapping.items():
            if xml_tag not in element:
                continue

            for child_dict in add_list(element.pop(xml_tag)):
                self.__format_maps(child_dict)

                if xml_tag == "ComponentMap":
                    consolidated_children.append(
                        self.__build_component_map(child_dict)
                    )
                elif xml_tag == "RepresentationMapping":
                    consolidated_children.append(
                        self.__build_representation_mapping(child_dict)
                    )
                else:
                    consolidated_children.append(target_class(**child_dict))

        if consolidated_children:
            element["maps"] = consolidated_children

        return element

    def __format_scheme(
        self, json_elem: Dict[str, Any], scheme: str, item: str
    ) -> Dict[str, ItemScheme]:
        elements: Dict[str, ItemScheme] = {}

        json_elem[scheme] = add_list(json_elem[scheme])
        for element in json_elem[scheme]:
            element["items"] = []

            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            element = self.__format_urls(element)
            if IS_EXTERNAL_REF in element:
                element[IS_EXTERNAL_REF_LOW] = (
                    element.pop(IS_EXTERNAL_REF) == "true"
                )
            if IS_FINAL in element:
                element[IS_FINAL_LOW] = element.pop(IS_FINAL) == "true"
            elif self.is_sdmx_30 and VERSION in element:
                element[IS_FINAL_LOW] = is_final(element[VERSION])
            if IS_PARTIAL in element:
                element[IS_PARTIAL_LOW] = element.pop(IS_PARTIAL) == "true"
            items = []
            if item in element:
                element[item] = add_list(element[item])
                items.extend(
                    [
                        self.__format_item(item_elem, item)
                        for item_elem in element[item]
                    ]
                )
                del element[item]
            element["items"] = items
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            element = self.__format_vtl(element)
            element = self.__format_vtl_references(element)
            if "xmlns" in element:
                del element["xmlns"]
            # Dynamic creation with specific class
            if scheme == VALUE_LIST:
                element["sdmx_type"] = VALUE_LIST_LOW
            result: ItemScheme = STRUCTURES_MAPPING[scheme](**element)
            elements[result.short_urn] = result

        return elements

    def __format_category(self, element: Dict[str, Any]) -> Category:
        """Recursively formats a Category element into the model.

        The dataflows and other references attached to the category are
        left empty here; they are filled in by the categorisation
        enrichment post-pass in ``format_structures``.
        """
        element = self.__format_annotations(element)
        element = self.__format_name_description(element)
        children = (
            [
                self.__format_category(child)
                for child in add_list(element[CATEGORY])
            ]
            if CATEGORY in element
            else []
        )
        return Category(
            id=element[ID],
            name=element.get(NAME.lower()),
            description=element.get(DESC.lower()),
            categories=tuple(children),
            annotations=tuple(element.get(ANNOTATIONS.lower(), ())),
        )

    def __format_category_scheme(
        self, json_elem: Dict[str, Any]
    ) -> Dict[str, CategoryScheme]:
        """Formats CategorySchemes into the model."""
        elements: Dict[str, CategoryScheme] = {}
        for element in add_list(json_elem[CATEGORY_SCHEME]):
            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            element = self.__format_urls(element)
            if IS_EXTERNAL_REF in element:
                element[IS_EXTERNAL_REF_LOW] = (
                    element.pop(IS_EXTERNAL_REF) == "true"
                )
            if IS_FINAL in element:
                element[IS_FINAL_LOW] = element.pop(IS_FINAL) == "true"
            elif self.is_sdmx_30 and VERSION in element:
                element[IS_FINAL_LOW] = is_final(element[VERSION])
            if IS_PARTIAL in element:
                element[IS_PARTIAL_LOW] = element.pop(IS_PARTIAL) == "true"
            items = (
                tuple(
                    self.__format_category(cat)
                    for cat in add_list(element[CATEGORY])
                )
                if CATEGORY in element
                else ()
            )
            element.pop(CATEGORY, None)
            element["items"] = items
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            if "xmlns" in element:
                del element["xmlns"]
            result = CategoryScheme(**element)
            elements[result.short_urn] = result
        return elements

    @staticmethod
    def __categorisation_ref(ref_elem: Any, maintainable: bool) -> str:
        """Resolves a categorisation Source/Target reference.

        Handles the 3.0/3.1 direct-URN string, the ``<URN>`` element
        form and the 2.1 ``<Ref>`` form. The output is the full URN
        string stored in ``Categorisation.source``/``.target``, matching
        the canonical form produced by the SDMX-JSON reader so that
        categorisations round-trip across formats.

        Args:
            ref_elem: The Source or Target element.
            maintainable: Whether the reference is to a maintainable
                artefact (Source) or to an item (Target).

        Returns:
            The full URN string representation of the reference.
        """
        ref: Union[Reference, ItemReference]
        if isinstance(ref_elem, dict) and REF in ref_elem:
            data = ref_elem[REF]
            if maintainable:
                ref = Reference(
                    sdmx_type=data[CLASS],
                    agency=data[AGENCY_ID],
                    id=data[ID],
                    version=data.get(VERSION, "1.0"),
                )
            else:
                ref = ItemReference(
                    sdmx_type=data[CLASS],
                    agency=data[AGENCY_ID],
                    id=data[PAR_ID],
                    version=data.get(PAR_VER, "1.0"),
                    item_id=data[ID],
                )
        elif isinstance(ref_elem, dict) and URN in ref_elem:
            ref = parse_urn(ref_elem[URN])
        else:
            ref = parse_urn(ref_elem)
        return create_full_urn(ref)

    def __format_categorisation(
        self, json_elem: Dict[str, Any]
    ) -> Dict[str, Categorisation]:
        """Formats Categorisations into the model."""
        elements: Dict[str, Categorisation] = {}
        for element in add_list(json_elem[CATEGORISATION]):
            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            element = self.__format_urls(element)
            if IS_EXTERNAL_REF in element:
                element[IS_EXTERNAL_REF_LOW] = (
                    element.pop(IS_EXTERNAL_REF) == "true"
                )
            if IS_FINAL in element:
                element[IS_FINAL_LOW] = element.pop(IS_FINAL) == "true"
            elif self.is_sdmx_30 and VERSION in element:
                element[IS_FINAL_LOW] = is_final(element[VERSION])
            element["source"] = self.__categorisation_ref(
                element.pop(SOURCE), maintainable=True
            )
            element["target"] = self.__categorisation_ref(
                element.pop(TARGET), maintainable=False
            )
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            if "xmlns" in element:
                del element["xmlns"]
            # Align with the SDMX-JSON reader, which always stores
            # annotations as a list, so categorisations compare equal
            # across formats even when no annotations are present.
            element.setdefault(ANNOTATIONS.lower(), [])
            result = Categorisation(**element)
            elements[result.short_urn] = result
        return elements

    def __format_level(self, level_elem: Dict[str, Any]) -> LevelType:
        """Recursively formats a Level element into a LevelType."""
        level_elem = self.__format_annotations(level_elem)
        level_elem = self.__format_name_description(level_elem)
        child = (
            self.__format_level(level_elem[LEVEL])
            if LEVEL in level_elem
            else None
        )
        return LevelType(
            id=level_elem[ID],
            name=level_elem.get(NAME.lower()),
            description=level_elem.get(DESC.lower()),
            annotations=tuple(level_elem.get(ANNOTATIONS.lower(), ())),
            level=child,
        )

    @staticmethod
    def __urn_from_code_ref(ref: Dict[str, Any]) -> str:
        """Builds a code URN from an SDMX-ML 2.1 <Code> reference."""
        return (
            "urn:sdmx:org.sdmx.infomodel.codelist.Code="
            f"{ref[AGENCY_ID]}:{ref[PAR_ID]}({ref[PAR_VER]}).{ref[ID]}"
        )

    def __format_code_ref(
        self, hc_elem: Dict[str, Any], aliases: Dict[str, str]
    ) -> str:
        """Resolves the referenced code URN (text, <Ref> or alias forms)."""
        if CODE in hc_elem:
            code_val = hc_elem[CODE]
            if isinstance(code_val, dict):
                return self.__urn_from_code_ref(code_val[REF])
            return _extract_text(code_val)
        alias = _extract_text(hc_elem[CODELIST_ALIAS_REF])
        code_id = str(hc_elem[CODE_ID][REF][ID])
        return f"{aliases[alias]}.{code_id}"

    @staticmethod
    def __format_level_ref(level_val: Any) -> str:
        """Resolves a per-code level id (text or <Ref> forms)."""
        if isinstance(level_val, dict):
            return str(level_val[REF][ID])
        return _extract_text(level_val)

    def __format_hierarchical_code(
        self,
        hc_elem: Dict[str, Any],
        aliases: Optional[Dict[str, str]] = None,
    ) -> HierarchicalCode:
        """Formats a HierarchicalCode element into the model."""
        aliases = aliases or {}
        hc_elem = self.__format_annotations(hc_elem)
        children = (
            [
                self.__format_hierarchical_code(child, aliases)
                for child in add_list(hc_elem[HIERARCHICAL_CODE])
            ]
            if HIERARCHICAL_CODE in hc_elem
            else []
        )
        rel_valid_from = (
            datetime.fromisoformat(hc_elem[VALID_FROM])
            if VALID_FROM in hc_elem
            else None
        )
        rel_valid_to = (
            datetime.fromisoformat(hc_elem[VALID_TO])
            if VALID_TO in hc_elem
            else None
        )
        level = (
            self.__format_level_ref(hc_elem[LEVEL])
            if LEVEL in hc_elem
            else None
        )
        return HierarchicalCode(
            id=hc_elem[ID],
            rel_valid_from=rel_valid_from,
            rel_valid_to=rel_valid_to,
            codes=tuple(children),
            annotations=tuple(hc_elem.get(ANNOTATIONS.lower(), ())),
            urn=self.__format_code_ref(hc_elem, aliases),
            level=level,
        )

    def __format_hierarchy(
        self, json_hierarchies: Dict[str, Any]
    ) -> Dict[str, Hierarchy]:
        """Formats the hierarchies (SDMX-ML 3.0/3.1) into the model."""
        elements: Dict[str, Hierarchy] = {}
        for element in add_list(json_hierarchies[HIERARCHY]):
            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            element = self.__format_urls(element)
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            if IS_EXTERNAL_REF in element:
                element[IS_EXTERNAL_REF_LOW] = (
                    element.pop(IS_EXTERNAL_REF) == "true"
                )
            has_formal_levels = (
                element.pop(HAS_FORMAL_LEVELS, "false") == "true"
            )
            level = (
                self.__format_level(element[LEVEL])
                if LEVEL in element
                else None
            )
            codes = (
                [
                    self.__format_hierarchical_code(child)
                    for child in add_list(element[HIERARCHICAL_CODE])
                ]
                if HIERARCHICAL_CODE in element
                else []
            )
            version = element.get(VERSION, "1.0")
            hierarchy = Hierarchy(
                id=element[ID],
                name=element.get(NAME.lower()),
                description=element.get(DESC.lower()),
                agency=element[AGENCY.lower()],
                version=version,
                valid_from=element.get(VALID_FROM_LOW),
                valid_to=element.get(VALID_TO_LOW),
                annotations=tuple(element.get(ANNOTATIONS.lower(), ())),
                is_external_reference=element.get(IS_EXTERNAL_REF_LOW, False),
                is_final=is_final(version),
                has_formal_levels=has_formal_levels,
                level=level,
                codes=tuple(codes),
            )
            elements[hierarchy.short_urn] = hierarchy
        return elements

    @staticmethod
    def __format_codelist_aliases(hcl: Dict[str, Any]) -> Dict[str, str]:
        """Maps each IncludedCodelist alias to a code-URN prefix."""
        aliases: Dict[str, str] = {}
        for incl in add_list(hcl.get(INCLUDED_CODELIST, [])):
            ref = incl[REF]
            aliases[incl[ALIAS]] = (
                "urn:sdmx:org.sdmx.infomodel.codelist.Code="
                f"{ref[AGENCY_ID]}:{ref[ID]}({ref.get(VERSION, '1.0')})"
            )
        return aliases

    def __format_inner_hierarchy(
        self,
        inner: Dict[str, Any],
        meta: Dict[str, Any],
        aliases: Dict[str, str],
    ) -> Hierarchy:
        """Formats an SDMX-ML 2.1 inner <Hierarchy> into the model.

        The wrapping codelist (the maintainable) carries the agency,
        version, validity, annotations and description, so those are taken
        from ``meta``; the inner element supplies the id, name and codes.
        """
        inner = self.__format_name_description(inner)
        has_formal_levels = inner.pop(LEVELED, "false") == "true"
        level = self.__format_level(inner[LEVEL]) if LEVEL in inner else None
        codes = (
            [
                self.__format_hierarchical_code(child, aliases)
                for child in add_list(inner[HIERARCHICAL_CODE])
            ]
            if HIERARCHICAL_CODE in inner
            else []
        )
        version = meta["version"]
        return Hierarchy(
            id=inner[ID],
            name=inner.get(NAME.lower()),
            description=meta["description"],
            agency=meta["agency"],
            version=version,
            valid_from=meta["valid_from"],
            valid_to=meta["valid_to"],
            annotations=meta["annotations"],
            is_external_reference=meta["is_external_reference"],
            is_final=is_final(version),
            has_formal_levels=has_formal_levels,
            level=level,
            codes=tuple(codes),
        )

    def __format_hierarchical_codelist(
        self, json_hcls: Dict[str, Any]
    ) -> Dict[str, Hierarchy]:
        """Formats SDMX-ML 2.1 HierarchicalCodelists into the model.

        Each inner ``<Hierarchy>`` becomes a separate pysdmx ``Hierarchy``,
        inheriting the maintainable metadata (agency, version, validity,
        description, annotations) of the wrapping codelist.
        """
        elements: Dict[str, Hierarchy] = {}
        for hcl in add_list(json_hcls[HIERARCHICAL_CODELIST]):
            aliases = self.__format_codelist_aliases(hcl)
            hcl = self.__format_annotations(hcl)
            hcl = self.__format_name_description(hcl)
            hcl = self.__format_agency(hcl)
            hcl = self.__format_validity(hcl)
            if IS_EXTERNAL_REF in hcl:
                hcl[IS_EXTERNAL_REF_LOW] = hcl.pop(IS_EXTERNAL_REF) == "true"
            meta = {
                "agency": hcl[AGENCY.lower()],
                "version": hcl.get(VERSION, "1.0"),
                "description": hcl.get(DESC.lower()),
                "valid_from": hcl.get(VALID_FROM_LOW),
                "valid_to": hcl.get(VALID_TO_LOW),
                "is_external_reference": hcl.get(IS_EXTERNAL_REF_LOW, False),
                "annotations": tuple(hcl.get(ANNOTATIONS.lower(), ())),
            }
            for inner in add_list(hcl.get(HIERARCHY, [])):
                hierarchy = self.__format_inner_hierarchy(inner, meta, aliases)
                elements[hierarchy.short_urn] = hierarchy
        return elements

    def __format_hierarchy_association(
        self, json_has: Dict[str, Any]
    ) -> Dict[str, HierarchyAssociation]:
        """Formats SDMX-ML 3.0/3.1 HierarchyAssociations into the model."""
        elements: Dict[str, HierarchyAssociation] = {}
        for element in add_list(json_has[HIERARCHY_ASSOCIATION]):
            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            element = self.__format_urls(element)
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            if IS_EXTERNAL_REF in element:
                element[IS_EXTERNAL_REF_LOW] = (
                    element.pop(IS_EXTERNAL_REF) == "true"
                )
            context = (
                _extract_text(element[CONTEXT_OBJECT])
                if CONTEXT_OBJECT in element
                else ""
            )
            version = element.get(VERSION, "1.0")
            ha = HierarchyAssociation(
                id=element[ID],
                name=element.get(NAME.lower()),
                description=element.get(DESC.lower()),
                agency=element[AGENCY.lower()],
                version=version,
                valid_from=element.get(VALID_FROM_LOW),
                valid_to=element.get(VALID_TO_LOW),
                annotations=tuple(element.get(ANNOTATIONS.lower(), ())),
                is_external_reference=element.get(IS_EXTERNAL_REF_LOW, False),
                is_final=is_final(version),
                hierarchy=_extract_text(element[LINKED_HIERARCHY]),
                component_ref=_extract_text(element[LINKED_OBJECT]),
                context_ref=context,
            )
            elements[ha.short_urn] = ha
        return elements

    def __format_schema(  # noqa: C901
        self, json_element: Dict[str, Any], schema: str, item: str
    ) -> Dict[str, Any]:
        """Formats the structures in json format.

        Args:
            json_element: The structures in json format
            schema: The scheme of the structures
            item: The item of the structures

        Returns:
            A dictionary with the structures formatted
        """
        schemas = {}

        json_element[item] = add_list(json_element[item])
        for element in json_element[item]:
            if URN.lower() in element and element[URN.lower()] is not None:
                short_urn = parse_urn(element[URN.lower()]).__str__()
            else:
                short_urn = Reference(
                    sdmx_type=item,
                    agency=element[AGENCY_ID],
                    id=element[ID],
                    version=element[VERSION],
                ).__str__()
            if METADATA in element:
                del element[METADATA]
            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            element = self.__format_urls(element)
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            element = self.__format_groups(element)
            element = self.__format_components(element)
            element = self.__format_maps(element)
            if item == PROV_AGREEMENT:
                element = self.__format_prov_agreement(element)
            if item in [CON_CONS, DATA_CONS]:
                element = self.__format_constraint(element)

            if "xmlns" in element:
                del element["xmlns"]
            if IS_EXTERNAL_REF in element:
                element[IS_EXTERNAL_REF_LOW] = element.pop(IS_EXTERNAL_REF)
                element[IS_EXTERNAL_REF_LOW] = (
                    str(element[IS_EXTERNAL_REF_LOW]).lower() == "true"
                )
            if IS_FINAL in element:
                element[IS_FINAL_LOW] = element.pop(IS_FINAL)
                element[IS_FINAL_LOW] = (
                    str(element[IS_FINAL_LOW]).lower() == "true"
                )
            elif self.is_sdmx_30 and VERSION in element:
                element[IS_FINAL_LOW] = is_final(element[VERSION])

            if item == DFW:
                if isinstance(element[STRUCTURE], str):
                    ref_obj = parse_urn(element[STRUCTURE])
                    reference_str = (
                        f"{ref_obj.sdmx_type}={ref_obj.agency}:"
                        f"{ref_obj.id}({ref_obj.version})"
                    )
                else:
                    ref_data = element[STRUCTURE][REF]
                    reference_str = (
                        f"{ref_data[CLASS]}={ref_data[AGENCY_ID]}"
                        f":{ref_data[ID]}({ref_data[VERSION]})"
                    )
                element[STRUCTURE] = reference_str

            structure = {key.lower(): value for key, value in element.items()}
            if schema == DSDS:
                if COMPS in structure:
                    structure[COMPS] = Components(structure[COMPS])
                else:
                    structure[COMPS] = Components([])
            if schema == REPRESENTATION_MAP:
                schemas[short_urn] = self.__build_representation_map(structure)
            else:
                schemas[short_urn] = STRUCTURES_MAPPING[schema](**structure)

        return schemas

    def format_structures(
        self, json_meta: Dict[str, Any]
    ) -> Sequence[Union[ItemScheme, DataStructureDefinition, Dataflow]]:
        """Formats the structures in JSON format.

        Args:
            json_meta: The structures in JSON format.

        Returns:
            A list with the formatted structures.
        """

        def process_structure(
            key: str,
            formatter: Callable[[Dict[str, Any]], Dict[Any, Any]],
            attr: Optional[str] = None,
        ) -> Dict[Any, Any]:
            """Helper function to process and store formatted structures."""
            if key in json_meta:
                formatted = formatter(json_meta[key])
                setattr(self, attr, formatted) if attr else None
                return formatted
            return {}

        structures = {
            ORGS: process_structure(ORGS, self.__format_orgs, "agencies"),
            AGENCIES: process_structure(
                AGENCIES, self.__format_orgs, "agencies"
            ),
            CLS: process_structure(
                CLS,
                lambda data: self.__format_scheme(data, CL, CODE),
                "codelists",
            ),
            VALUE_LISTS: process_structure(
                VALUE_LISTS,
                lambda data: self.__format_scheme(
                    data, VALUE_LIST, VALUE_ITEM
                ),
                "valuelists",
            ),
            HIERARCHIES: process_structure(
                HIERARCHIES,
                self.__format_hierarchy,
            ),
            HIERARCHICAL_CODELISTS: process_structure(
                HIERARCHICAL_CODELISTS,
                self.__format_hierarchical_codelist,
            ),
            HIERARCHY_ASSOCIATIONS: process_structure(
                HIERARCHY_ASSOCIATIONS,
                self.__format_hierarchy_association,
            ),
            CON_SCHEMES: process_structure(
                CON_SCHEMES,
                lambda data: self.__format_scheme(data, CS, CON),
                "concepts",
            ),
            CONCEPTS: process_structure(
                CONCEPTS,
                lambda data: self.__format_scheme(data, CS, CON),
                "concepts",
            ),
            DSDS: process_structure(
                DSDS,
                lambda data: self.__format_schema(data, DSDS, DSD),
                "datastructures",
            ),
            DFWS: process_structure(
                DFWS,
                lambda data: self.__format_schema(data, DFWS, DFW),
                "dataflows",
            ),
            PROV_AGREEMENTS: process_structure(
                PROV_AGREEMENTS,
                lambda data: self.__format_schema(
                    data, PROV_AGREEMENTS, PROV_AGREEMENT
                ),
            ),
            CATEGORY_SCHEMES: process_structure(
                CATEGORY_SCHEMES,
                self.__format_category_scheme,
                "category_schemes",
            ),
            CATEGORISATIONS: process_structure(
                CATEGORISATIONS,
                self.__format_categorisation,
                "categorisations",
            ),
            VTLMAPPINGS: process_structure(
                VTLMAPPINGS,
                lambda data: self.__format_scheme(
                    data,
                    VTL_MAPPING_SCHEME,
                    VTLMAPPING,
                ),
                "vtl_mappings",
            ),
            VTLMAPPING_SCHEMES: process_structure(
                VTLMAPPING_SCHEMES,
                lambda data: self.__format_scheme(
                    data,
                    VTL_MAPPING_SCHEME,
                    VTLMAPPING,
                ),
                "vtl_mappings",
            ),
            RULESETS: process_structure(
                RULESETS,
                lambda data: self.__format_scheme(data, RULE_SCHEME, RULE),
                "rulesets",
            ),
            RULE_SCHEMES: process_structure(
                RULE_SCHEMES,
                lambda data: self.__format_scheme(data, RULE_SCHEME, RULE),
                "rulesets",
            ),
            UDOS: process_structure(
                UDOS,
                lambda data: self.__format_scheme(data, UDO_SCHEME, UDO),
                "udos",
            ),
            UDO_SCHEMES: process_structure(
                UDO_SCHEMES,
                lambda data: self.__format_scheme(data, UDO_SCHEME, UDO),
                "udos",
            ),
            NAME_PERS: process_structure(
                NAME_PERS,
                lambda data: self.__format_scheme(
                    data, NAME_PER_SCHEME, NAME_PER
                ),
                "name_personalisations",
            ),
            NAME_PER_SCHEMES: process_structure(
                NAME_PER_SCHEMES,
                lambda data: self.__format_scheme(
                    data, NAME_PER_SCHEME, NAME_PER
                ),
                "name_personalisations",
            ),
            CUSTOM_TYPES: process_structure(
                CUSTOM_TYPES,
                lambda data: self.__format_scheme(
                    data, CUSTOM_TYPE_SCHEME, CUSTOM_TYPE
                ),
                "custom_types",
            ),
            CUSTOM_TYPE_SCHEMES: process_structure(
                CUSTOM_TYPE_SCHEMES,
                lambda data: self.__format_scheme(
                    data, CUSTOM_TYPE_SCHEME, CUSTOM_TYPE
                ),
                "custom_types",
            ),
            TRANSFORMATIONS: process_structure(
                TRANSFORMATIONS,
                lambda data: self.__format_scheme(
                    data,
                    TRANS_SCHEME,
                    TRANSFORMATION,
                ),
                "transformations",
            ),
            STRUCTURE_MAPS: process_structure(
                STRUCTURE_MAPS,
                lambda data: self.__format_schema(
                    data, STRUCTURE_MAP, STRUCTURE_MAP
                ),
                "structure_maps",
            ),
            COMPONENT_MAPS: process_structure(
                COMPONENT_MAPS,
                lambda data: self.__format_schema(
                    data, COMPONENT_MAP, COMPONENT_MAP
                ),
                "component_maps",
            ),
            FIXED_VALUE_MAPS: process_structure(
                FIXED_VALUE_MAPS,
                lambda data: self.__format_schema(
                    data, FIXED_VALUE_MAP, FIXED_VALUE_MAP
                ),
                "fixed_value_maps",
            ),
            REPRESENTATION_MAPS: process_structure(
                REPRESENTATION_MAPS,
                lambda data: self.__format_schema(
                    data, REPRESENTATION_MAP, REPRESENTATION_MAP
                ),
                "representation_maps",
            ),
            CONSTRAINTS: process_structure(
                CONSTRAINTS,
                lambda data: self.__format_schema(data, CONSTRAINTS, CON_CONS),
                "constraints",
            ),
            DATA_CONSTRAINTS: process_structure(
                DATA_CONSTRAINTS,
                lambda data: self.__format_schema(
                    data, DATA_CONSTRAINTS, DATA_CONS
                ),
                "constraints",
            ),
            TRANS_SCHEMES: process_structure(
                TRANS_SCHEMES,
                lambda data: self.__format_scheme(
                    data,
                    TRANS_SCHEME,
                    TRANSFORMATION,
                ),
                "transformations",
            ),
        }
        self.__enrich_category_schemes(structures.get(CATEGORY_SCHEMES, {}))
        return [
            compound
            for value in structures.values()
            if value
            for compound in value.values()
        ]

    def __rebuild_category(
        self,
        category: Category,
        parent_path: str,
        flows: Dict[str, List[DataflowRef]],
        others: Dict[str, List[Union[ItemReference, Reference]]],
    ) -> Category:
        """Rebuilds a category attaching the categorised references.

        The category tree is immutable, so a new tree is built by path.
        """
        path = f"{parent_path}.{category.id}" if parent_path else category.id
        return Category(
            id=category.id,
            name=category.name,
            description=category.description,
            annotations=category.annotations,
            categories=tuple(
                self.__rebuild_category(child, path, flows, others)
                for child in category.categories
            ),
            dataflows=tuple(flows.get(path, ())),
            other_references=tuple(others.get(path, ())),
        )

    def __enrich_category_schemes(
        self, category_schemes: Dict[str, CategoryScheme]
    ) -> None:
        """Attaches categorised dataflows/references to category schemes.

        This mirrors the SDMX-JSON behaviour: each categorisation whose
        target is a category in one of the schemes contributes either a
        dataflow (when the source is a dataflow) or a reference to the
        targeted category. As the model is immutable, the affected
        category trees are rebuilt in place.
        """
        if not category_schemes or not self.categorisations:
            return
        flows: Dict[str, Dict[str, List[DataflowRef]]] = {}
        others: Dict[
            str, Dict[str, List[Union[ItemReference, Reference]]]
        ] = {}
        for cat in self.categorisations.values():
            target = parse_urn(cat.target)
            scheme_urn = (
                f"CategoryScheme={target.agency}:{target.id}({target.version})"
            )
            if scheme_urn not in category_schemes:
                continue
            path = cat.target[cat.target.find(")") + 2 :]
            source = parse_urn(cat.source)
            if source.sdmx_type == "Dataflow":
                flow = self.__resolve_dataflow(source)
                flows.setdefault(scheme_urn, {}).setdefault(path, []).append(
                    flow
                )
            else:
                others.setdefault(scheme_urn, {}).setdefault(path, []).append(
                    source
                )
        for urn, scheme in list(category_schemes.items()):
            scheme_flows = flows.get(urn, {})
            scheme_others = others.get(urn, {})
            if not scheme_flows and not scheme_others:
                continue
            category_schemes[urn] = replace(
                scheme,
                items=tuple(
                    self.__rebuild_category(
                        cat, "", scheme_flows, scheme_others
                    )
                    for cat in scheme.items
                ),
            )

    def __resolve_dataflow(
        self, source: Union[Reference, ItemReference]
    ) -> DataflowRef:
        """Resolves a dataflow reference to a DataflowRef.

        This mirrors the SDMX-JSON behaviour, which always emits a
        ``DataflowRef``. If the referenced dataflow is present in the
        message, the resolved flow's name is carried over; otherwise a
        lightweight ``DataflowRef`` (without a name) is built.
        """
        urn = f"Dataflow={source.agency}:{source.id}({source.version})"
        if urn in self.dataflows:
            flow = self.dataflows[urn]
            agency = (
                flow.agency.id
                if isinstance(flow.agency, Agency)
                else flow.agency
            )
            return DataflowRef(
                agency=agency,
                id=flow.id,
                version=flow.version,
                name=flow.name,
            )
        return DataflowRef(
            agency=source.agency,
            id=source.id,
            version=source.version,
        )
