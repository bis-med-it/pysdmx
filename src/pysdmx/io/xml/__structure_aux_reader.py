"""Parsers for reading metadata."""

from datetime import datetime
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.io.xml.__tokens import (
    AGENCIES,
    AGENCY,
    AGENCY_ID,
    AGENCY_SCHEME,
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
    CL,
    CL_LOW,
    CLASS,
    CLS,
    CODE,
    CODES_LOW,
    COMPS,
    CON,
    CON_ID,
    CON_LOW,
    CON_ROLE,
    CON_SCHEMES,
    CONCEPTS,
    CONTACT,
    CORE_REP,
    CS,
    CUSTOM_TYPE,
    CUSTOM_TYPE_SCHEME,
    CUSTOM_TYPE_SCHEMES,
    CUSTOM_TYPES,
    DEPARTMENT,
    DESC,
    DFW,
    DFW_ALIAS_LOW,
    DFW_LOW,
    DFWS,
    DIM,
    DIM_LIST,
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
    GROUP,
    GROUP_DIM,
    ID,
    IS_EXTERNAL_REF,
    IS_EXTERNAL_REF_LOW,
    IS_FINAL,
    IS_FINAL_LOW,
    IS_PARTIAL,
    IS_PARTIAL_LOW,
    LINK,
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
    NAME,
    NAME_PER,
    NAME_PER_SCHEME,
    NAME_PER_SCHEMES,
    NAME_PERS,
    OBSERVATION,
    ORGS,
    PAR_ID,
    PAR_VER,
    PRIM_MEASURE,
    REF,
    REQUIRED,
    ROLE,
    RULE,
    RULE_SCHEME,
    RULE_SCHEMES,
    RULESETS,
    SER_URL,
    SER_URL_LOW,
    STR_URL,
    STR_URL_LOW,
    STRUCTURE,
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
    VALUE_ITEM,
    VALUE_LIST,
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
    Code,
    Codelist,
    Concept,
    ConceptScheme,
    DataType,
    Facets,
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
from pysdmx.util import find_by_urn, parse_urn

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
    NAME_PER_SCHEME: NamePersonalisationScheme,
    CUSTOM_TYPE_SCHEME: CustomTypeScheme,
}
ITEMS_CLASSES = {
    AGENCY: Agency,
    CODE: Code,
    VALUE_ITEM: Code,
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

COMP_TYPES = [DIM, ATT, PRIM_MEASURE, MEASURE, GROUP_DIM]

ROLE_MAPPING = {
    DIM: Role.DIMENSION,
    ATT: Role.ATTRIBUTE,
    PRIM_MEASURE: Role.MEASURE,
    MEASURE: Role.MEASURE,
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
    concepts: Dict[str, ConceptScheme] = {}
    datastructures: Dict[str, DataStructureDefinition] = {}
    dataflows: Dict[str, Dataflow] = {}
    rulesets: Dict[str, RulesetScheme] = {}
    udos: Dict[str, UserDefinedOperatorScheme] = {}
    vtl_mappings: Dict[str, VtlMappingScheme] = {}
    name_personalisations: Dict[str, NamePersonalisationScheme] = {}
    custom_types: Dict[str, CustomTypeScheme] = {}
    transformations: Dict[str, TransformationScheme] = {}
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
        for key, _value in json_fac.items():
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
            ag_sch = self.__format_scheme(
                e,
                AGENCY_SCHEME,
                AGENCY,
            )
            orgs = {**orgs, **ag_sch}
        return orgs

    def __format_representation(
        self, json_rep: Dict[str, Any], json_obj: Dict[str, Any]
    ) -> None:
        """Formats the representation in the JSON Representation."""
        if TEXT_FORMAT in json_rep:
            self.__format_facets(json_rep[TEXT_FORMAT], json_obj)

        if ENUM in json_rep and len(self.codelists) > 0:
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
                codelist = find_by_urn(list(self.codelists.values()), str(ref))
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

    def __format_con_id(self, concept_ref: Dict[str, Any]) -> Dict[str, Any]:
        rep = {}
        if isinstance(concept_ref, str):
            item_reference = parse_urn(concept_ref)
            scheme_reference = Reference(
                sdmx_type=CS,
                agency=item_reference.agency,
                id=item_reference.id,
                version=item_reference.version,
            )
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
                agency=concept_ref[AGENCY_ID],
                id=concept_ref[PAR_ID],
                version=concept_ref[PAR_VER],
            )

        concept_scheme = self.concepts.get(str(scheme_reference))
        if concept_scheme is None:
            return {CON: item_reference}
        for con in concept_scheme.concepts:
            if isinstance(concept_ref, str):
                if con.id == item_reference.item_id:
                    rep[CON] = con
                    break
            elif con.id == concept_ref[ID]:
                rep[CON] = con
                break
        if CON not in rep:
            return {CON: item_reference}
        return rep

    @staticmethod
    def __get_attachment_level(attribute: Dict[str, Any]) -> str:
        if DIM in attribute:
            dims = add_list(attribute[DIM])
            if dims and isinstance(dims[0], dict):
                dims = [dim[REF][ID] for dim in dims]
            att_level = ",".join(dims)
            # AttachmentGroup can only appear as sequence of the Dimension,
            # therefore we need to check first if a Dimension is present,
            # then the AttachmentGroup
            if ATTACH_GROUP in attribute:
                raise NotImplementedError(
                    "Attribute relationships with Dimension "
                    "and AttachmentGroup is not supported."
                )
        elif GROUP in attribute:
            raise NotImplementedError(
                "Attribute relationships with Group is not supported."
            )
        elif OBSERVATION in attribute or PRIM_MEASURE in attribute:
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
        self, json_rep: Dict[str, Any], json_obj: Dict[str, Any]
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
        if REF in json_rep:
            json_rep.pop(REF)
        json_obj.pop(DFW)
        if self.dataflows:
            for dataflow in self.dataflows.values():
                if dataflow.id == dataflow_ref[ID]:
                    json_obj[DFW_LOW] = dataflow

    def __format_component(
        self, comp: Dict[str, Any], role: Role
    ) -> Component:
        comp[ROLE.lower()] = role
        comp[REQUIRED] = True

        self.__format_local_rep(comp) if LOCAL_REP in comp else None

        if LINK in comp:
            del comp[LINK]
        if REF in comp[CON_ID]:
            concept_id = self.__format_con_id(comp[CON_ID][REF])
        else:
            concept_id = self.__format_con_id(comp[CON_ID])
        comp[CON_LOW] = concept_id.pop(CON)
        del comp[CON_ID]

        # Attribute Handling
        if ATT_REL in comp:
            comp[ATT_LVL] = self.__get_attachment_level(comp[ATT_REL])
            del comp[ATT_REL]

        if ME_REL in comp:
            del comp[ME_REL]

        if AS_STATUS in comp or USAGE in comp:
            status_key = AS_STATUS if AS_STATUS in comp else USAGE
            if (
                comp[status_key] != MANDATORY
                and comp[status_key] != MANDATORY_LOW
            ):
                comp[REQUIRED] = False
            del comp[status_key]

        if "position" in comp:
            del comp["position"]

        if ANNOTATIONS in comp:
            del comp[ANNOTATIONS]

        if CON_ROLE in comp:
            del comp[CON_ROLE]

        return Component(**comp)

    def __format_component_lists(
        self, element: Dict[str, Any]
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
            )
            comp_list.append(formatted_comp)

        return comp_list

    def __format_components(self, element: Dict[str, Any]) -> Dict[str, Any]:
        if DSD_COMPS in element:
            element[COMPS] = []
            comps = element[DSD_COMPS]

            for comp_list in [DIM_LIST, ME_LIST, GROUP, ATT_LIST]:
                if comp_list == GROUP and comp_list in comps:
                    del comps[GROUP]

                elif comp_list in comps:
                    fmt_comps = self.__format_component_lists(comps[comp_list])
                    element[COMPS].extend(fmt_comps)

            element[COMPS] = Components(element[COMPS])
            del element[DSD_COMPS]

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
            contacts = []
            for e in item_json_info[CONTACT]:
                contacts.append(self.__format_contact(e))
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

    def __format_is_final_30(
        self, json_elem: Dict[str, Any]
    ) -> Dict[str, Any]:
        if self.is_sdmx_30:
            # Default version value is 1.0, in SDMX-ML 3.0 we need to set
            # is_final as True if the version does not have an EXTENSION
            # (see Technical Notes SDMX 3.0)
            json_elem[IS_FINAL_LOW] = (
                "-" not in json_elem[VERSION] if VERSION in json_elem else True
            )
        return json_elem

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
            if IS_PARTIAL in element:
                element[IS_PARTIAL_LOW] = element.pop(IS_PARTIAL) == "true"
            items = []
            if item in element:
                element[item] = add_list(element[item])
                for item_elem in element[item]:
                    # Dynamic
                    items.append(self.__format_item(item_elem, item))
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
                element["sdmx_type"] = "valuelist"
            element = self.__format_is_final_30(element)
            result: ItemScheme = STRUCTURES_MAPPING[scheme](**element)
            elements[result.short_urn] = result

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
            element = self.__format_components(element)

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
            structure = self.__format_is_final_30(structure)
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
        return [
            compound
            for value in structures.values()
            if value
            for compound in value.values()
        ]
