"""Parsers for reading metadata."""

from datetime import datetime
from typing import Any, Dict, List, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.errors import Invalid
from pysdmx.io.xml.sdmx21.__tokens import (
    AGENCIES,
    AGENCY,
    AGENCY_ID,
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
    CL,
    CLASS,
    CLS,
    CODE,
    CODES_LOW,
    COMPS,
    CON,
    CON_ID,
    CON_LOW,
    CONCEPTS,
    CONTACT,
    CORE_REP,
    CS,
    DEPARTMENT,
    DESC,
    DFW,
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
    LOCAL_CODES_LOW,
    LOCAL_DTYPE,
    LOCAL_FACETS_LOW,
    LOCAL_REP,
    MANDATORY,
    ME_LIST,
    NAME,
    ORGS,
    PAR_ID,
    PAR_VER,
    PRIM_MEASURE,
    REF,
    REQUIRED,
    ROLE,
    SER_URL,
    SER_URL_LOW,
    STR_URL,
    STR_URL_LOW,
    STRUCTURE,
    STRUCTURES,
    TELEPHONE,
    TELEPHONES,
    TEXT,
    TEXT_FORMAT,
    TEXT_TYPE,
    TIME_DIM,
    TITLE,
    TRANS_SCHEME,
    TRANSFORMATION,
    TRANSFORMATIONS,
    TYPE,
    URI,
    URIS,
    URL,
    URN,
    VALID_FROM,
    VALID_FROM_LOW,
    VALID_TO,
    VALID_TO_LOW,
    VERSION,
)
from pysdmx.io.xml.sdmx21.reader.__parse_xml import parse_xml
from pysdmx.io.xml.utils import add_list
from pysdmx.model import (
    AgencyScheme,
    Code,
    Codelist,
    Concept,
    ConceptScheme,
    DataType,
    Facets,
)
from pysdmx.model.__base import Agency, Annotation, Contact, Item, ItemScheme
from pysdmx.model.dataflow import (
    Component,
    Components,
    Dataflow,
    DataStructureDefinition,
    Role,
)
from pysdmx.model.vtl import Transformation, TransformationScheme
from pysdmx.util import ItemReference, Reference, find_by_urn, parse_urn

STRUCTURES_MAPPING = {
    CL: Codelist,
    AGENCIES: AgencyScheme,
    CS: ConceptScheme,
    DFWS: Dataflow,
    DSDS: DataStructureDefinition,
    TRANS_SCHEME: TransformationScheme,
}
ITEMS_CLASSES = {
    AGENCY: Agency,
    CODE: Code,
    CON: Concept,
    TRANSFORMATION: Transformation,
}

COMP_TYPES = [DIM, ATT, PRIM_MEASURE, GROUP_DIM]

ROLE_MAPPING = {
    DIM: Role.DIMENSION,
    ATT: Role.ATTRIBUTE,
    PRIM_MEASURE: Role.MEASURE,
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


class StructureParser(Struct):
    """StructureParser class for SDMX-ML 2.1."""

    agencies: Dict[str, Any] = {}
    codelists: Dict[str, Any] = {}
    concepts: Dict[str, Any] = {}
    datastructures: Dict[str, Any] = {}
    dataflows: Dict[str, Any] = {}

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
                AGENCIES,
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
            ref = json_rep[ENUM].get(REF, json_rep[ENUM])

            if "URN" in ref:
                codelist = find_by_urn(
                    list(self.codelists.values()), ref["URN"]
                ).codes

            else:
                short_urn = str(
                    Reference(
                        sdmx_type=ref[CLASS],
                        agency=ref[AGENCY_ID],
                        id=ref[ID],
                        version=ref[VERSION],
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
            if con.id == concept_ref[ID]:
                rep[CON] = con
                break
        if CON not in rep:
            return {CON: item_reference}
        return rep

    @staticmethod
    def __format_relationship(json_rel: Dict[str, Any]) -> Optional[str]:
        att_level = None

        for scheme in [DIM, PRIM_MEASURE]:
            if scheme in json_rel:
                if scheme == DIM:
                    dims = add_list(json_rel[DIM])
                    dims = [dim[REF][ID] for dim in dims]
                    att_level = ",".join(dims)
                else:
                    att_level = "O"

        return att_level

    def __format_component(
        self, comp: Dict[str, Any], role: Role
    ) -> Component:
        comp[ROLE.lower()] = role
        comp[REQUIRED] = True

        self.__format_local_rep(comp) if LOCAL_REP in comp else None

        concept_id = self.__format_con_id(comp[CON_ID][REF])
        comp[CON_LOW] = concept_id.pop(CON)
        del comp[CON_ID]

        # Attribute Handling
        if ATT_REL in comp:
            comp[ATT_LVL] = self.__format_relationship(comp[ATT_REL])
            del comp[ATT_REL]

        if AS_STATUS in comp:
            if comp[AS_STATUS] != MANDATORY:
                comp[REQUIRED] = False
            del comp[AS_STATUS]

        if "position" in comp:
            del comp["position"]

        if ANNOTATIONS in comp:
            del comp[ANNOTATIONS]

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
            formatted_comp = self.__format_component(comp, role)
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

    @staticmethod
    def __format_vtl(json_vtl: Dict[str, Any]) -> Dict[str, Any]:
        if "isPersistent" in json_vtl:
            json_vtl["is_persistent"] = json_vtl.pop("isPersistent")
        if "Expression" in json_vtl:
            json_vtl["expression"] = json_vtl.pop("Expression")
        if "Result" in json_vtl:
            json_vtl["result"] = json_vtl.pop("Result")
        if "vtlVersion" in json_vtl:
            json_vtl["vtl_version"] = json_vtl.pop("vtlVersion")
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

        item_json_info = self.__format_vtl(item_json_info)

        return ITEMS_CLASSES[item_name_class](**item_json_info)

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
            element[item] = add_list(element[item])
            items = []
            for item_elem in element[item]:
                # Dynamic
                items.append(self.__format_item(item_elem, item))
            del element[item]
            element["items"] = items
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            element = self.__format_vtl(element)
            if "xmlns" in element:
                del element["xmlns"]
            # Dynamic creation with specific class
            result: ItemScheme = STRUCTURES_MAPPING[scheme](**element)
            elements[result.short_urn] = result

        return elements

    def __format_schema(
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
            schemas[short_urn] = STRUCTURES_MAPPING[schema](**structure)

        return schemas

    def format_structures(
        self, json_meta: Dict[str, Any]
    ) -> Sequence[Union[ItemScheme, DataStructureDefinition, Dataflow]]:
        """Formats the structures in json format.

        Args:
            json_meta: The structures in json format

        Returns:
            A dictionary with the structures formatted
        """
        # Reset dict to store metadata
        structures = {}

        if ORGS in json_meta:
            structures[ORGS] = self.__format_orgs(json_meta[ORGS])
            self.agencies = structures[ORGS]
        if CLS in json_meta:
            structures[CLS] = self.__format_scheme(json_meta[CLS], CL, CODE)
            self.codelists = structures[CLS]
        if CONCEPTS in json_meta:
            structures[CONCEPTS] = self.__format_scheme(
                json_meta[CONCEPTS], CS, CON
            )
            self.concepts = structures[CONCEPTS]
        if DSDS in json_meta:
            structures[DSDS] = self.__format_schema(json_meta[DSDS], DSDS, DSD)
            self.datastructures = structures[DSDS]
        if DFWS in json_meta:
            structures[DFWS] = self.__format_schema(json_meta[DFWS], DFWS, DFW)

        if TRANSFORMATIONS in json_meta:
            structures[TRANSFORMATIONS] = self.__format_scheme(
                json_meta[TRANSFORMATIONS], TRANS_SCHEME, TRANSFORMATION
            )
        # Reset global variables
        result = []
        for value in structures.values():
            for compound in value.values():
                result.append(compound)

        return result


def read(
    input_str: str,
    validate: bool = True,
) -> Sequence[Union[ItemScheme, DataStructureDefinition, Dataflow]]:
    """Reads an SDMX-ML 2.1 Structure data and returns the structures.

    Args:
        input_str: SDMX-ML data to read.
        validate: If True, the XML data will be validated against the XSD.

    Returns:
        dict: Dictionary with the parsed structures.
    """
    dict_info = parse_xml(input_str, validate)
    if STRUCTURE not in dict_info:
        raise Invalid("This SDMX document is not SDMX-ML 2.1 Structure.")
    return StructureParser().format_structures(
        dict_info[STRUCTURE][STRUCTURES]
    )
