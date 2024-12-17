"""Parsers for reading metadata."""

from datetime import datetime
from typing import Any, Dict, List

from msgspec import Struct

from pysdmx.io.xml.sdmx21.__parsing_config import (
    AS_STATUS,
    ATT,
    ATT_LIST,
    ATT_LVL,
    ATT_REL,
    CODES_LOW,
    COMPS,
    CON_ID,
    CON_LOW,
    CORE_REP,
    DIM,
    DIM_LIST,
    DSD_COMPS,
    DTYPE,
    ENUM,
    GROUP,
    GROUP_DIM,
    LOCAL_CODES_LOW,
    LOCAL_DTYPE,
    LOCAL_FACETS_LOW,
    LOCAL_REP,
    MANDATORY,
    ME_LIST,
    PRIM_MEASURE,
    REF,
    REQUIRED,
    TEXT_FORMAT,
    TIME_DIM, ENUM_FORMAT, CLASS,
)
from pysdmx.io.xml.sdmx21.reader.__utils import (
    AGENCIES,
    AGENCY,
    AGENCY_ID,
    ANNOTATION,
    ANNOTATION_TEXT,
    ANNOTATION_TITLE,
    ANNOTATION_TYPE,
    ANNOTATION_URL,
    ANNOTATIONS,
    CL,
    CLS,
    CODE,
    CON,
    CONTACT,
    CS,
    DEPARTMENT,
    DESC,
    DFW,
    DFWS,
    DSD,
    DSDS,
    EMAIL,
    EMAILS,
    FACETS,
    FacetType,
    FAX,
    FAXES,
    ID,
    IS_EXTERNAL_REF,
    IS_EXTERNAL_REF_LOW,
    IS_FINAL,
    IS_FINAL_LOW,
    IS_PARTIAL,
    IS_PARTIAL_LOW,
    NAME,
    ROLE,
    SER_URL,
    SER_URL_LOW,
    STR,
    STR_URL,
    STR_URL_LOW,
    TELEPHONE,
    TELEPHONES,
    TEXT,
    TEXT_TYPE,
    TITLE,
    TRANS_SCHEME,
    TRANSFORMATION,
    TRANSFORMATIONS,
    TYPE,
    unique_id,
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
from pysdmx.io.xml.utils import add_list
from pysdmx.model import (
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
from pysdmx.model.message import CONCEPTS, ORGS
from pysdmx.model.vtl import Transformation, TransformationScheme
from pysdmx.util import find_by_urn, parse_urn

STRUCTURES_MAPPING = {
    CL: Codelist,
    AGENCIES: ItemScheme,
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

components: Dict[str, Any] = {}


class StructureParser(Struct):
    """StructureParser class for SDMX-ML 2.1."""

    agencies: Dict[str, Any] = {}
    codelists: Dict[str, Any] = {}
    concepts: Dict[str, Any] = {}
    datastructures: Dict[str, Any] = {}
    dataflows: Dict[str, Any] = {}

    def __extract_text(self, element: Any) -> str:
        """Extracts the text from the element.

        Args:
            element: The element to extract the text from

        Returns:
            The text extracted from the element
        """
        if isinstance(element, dict) and "#text" in element:
            element = element["#text"]
        return element

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
                    json_contact[v] = self.__extract_text(json_contact.pop(k))
                    continue
                field_info = add_list(json_contact.pop(k))
                for i, element in enumerate(field_info):
                    field_info[i] = self.__extract_text(element)
                json_contact[v] = field_info

        return Contact(**json_contact)

    def __format_annotations(self, item_elem: Any) -> Dict[str, Any]:
        """Formats the annotations in the item_elem.

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
                e[TEXT] = self.__extract_text(e[ANNOTATION_TEXT])
                del e[ANNOTATION_TEXT]
            if ANNOTATION_URL in e:
                e[URL] = e.pop(ANNOTATION_URL)

            annotations.append(Annotation(**e))

        item_elem[ANNOTATIONS.lower()] = annotations
        del item_elem[ANNOTATIONS]

        return item_elem

    def __format_name_description(self, element: Any) -> Dict[str, Any]:
        node = [NAME, DESC]
        for field in node:
            if field in element:
                element[field.lower()] = self.__extract_text(element[field])
                del element[field]
        return element

    @staticmethod
    def __format_facets(
        json_fac: Dict[str, Any], json_obj: Dict[str, Any]
    ) -> None:
        """Formats the facets in the json_fac to be stored in json_obj.

        Args:
            json_fac: The element with the facets to be formatted
            json_obj: The element to store the formatted facets
        """
        if json_fac is None:
            return
        for key, _value in json_fac.items():
            if key == TEXT_TYPE and json_fac[TEXT_TYPE] in list(DataType):
                json_obj["dtype"] = DataType(json_fac[TEXT_TYPE])

            if key in FacetType:
                facet_kwargs = {
                    FacetType[k]: v
                    for k, v in json_fac.items()
                    if k in FacetType
                }
                json_obj[FACETS.lower()] = Facets(**facet_kwargs)

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
        json_orgs = add_list(json_orgs)  # type: ignore[assignment]
        for e in json_orgs:
            ag_sch = self.__format_scheme(
                e, AGENCIES, AGENCY  # type: ignore[arg-type]
            )
            orgs = {**orgs, **ag_sch}
        return orgs

    def __format_validity(self, element: Dict[str, Any]) -> Dict[str, Any]:
        if "validFrom" in element:
            element["valid_from"] = element.pop("validFrom")
        if "validTo" in element:
            element["valid_to"] = element.pop("validTo")
        return element

    def __format_representation(
        self, json_rep: Dict[str, Any], json_obj: Dict[str, Any]
    ) -> None:
        """Formats the representation in the json_rep."""
        if TEXT_FORMAT in json_rep:
            self.__format_facets(json_rep[TEXT_FORMAT], json_obj)

        if ENUM in json_rep and len(self.codelists) > 0:
            ref = json_rep[ENUM].get(REF, json_rep[ENUM])

            if "URN" in ref:
                codelist = find_by_urn(
                    list(self.codelists.values()), ref["URN"]
                ).codes

            else:
                id = unique_id(ref[AGENCY_ID], ref[ID], ref[VERSION])
                codelist = self.codelists[id]

            json_obj[CODES_LOW] = codelist
        if ENUM_FORMAT in json_rep:
            self.__format_facets(json_rep[ENUM_FORMAT], json_obj)

    def __format_validity(self, element: Dict[str, Any]) -> Dict[str, Any]:
        """Formats the version in the element.

        Args:
            element: The element with the version to be formatted

        Returns:
            element with the version, validFrom and validTo formatted
        """
        element[VERSION] = element.pop(VERSION)

        if VALID_FROM in element:
            element[VALID_FROM] = datetime.fromisoformat(element[VALID_FROM])
            element[VALID_FROM_LOW] = element.pop(VALID_FROM)

        if VALID_TO in element:
            element[VALID_TO] = datetime.fromisoformat(element[VALID_TO])
            element[VALID_TO_LOW] = element.pop(VALID_TO)

        return element

    def __format_local_rep(self, representation_info: Dict[str, Any]) -> None:
        rep: Dict[str, Any] = {}

        if LOCAL_REP in representation_info:
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
        id = concept_ref[ID]

        rep[CON] = self.concepts[id]
        return rep

    def __format_relationship(
        self, json_rel: Dict[str, Any]
    ) -> Dict[str, Any]:
        rels: Dict[str, Any] = {}

        for scheme in [DIM, PRIM_MEASURE]:
            comp_list = DIM_LIST if scheme == DIM else ME_LIST
            if scheme in json_rel:
                rel_list = add_list(json_rel[scheme])
                for element in rel_list:
                    element_id = element[REF][ID]
                    component = next(
                        (
                            comp
                            for comp in components[comp_list]
                            if comp.id == element_id
                        ),
                        None,
                    )
                    rels[element_id] = component

        return rels

    def __format_component(
        self, comp: Dict[str, Any], role: Role
    ) -> Component:
        comp[ROLE.lower()] = role
        comp[REQUIRED] = True

        self.__format_local_rep(comp)

        rep = self.__format_con_id(comp[CON_ID][REF])
        comp[CON_LOW] = rep.pop(CON)
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

        if URN in comp:
            comp[URN.lower()] = comp.pop(URN)

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
            components.clear()

            for comp_list in [DIM_LIST, ME_LIST, GROUP, ATT_LIST]:
                if comp_list == GROUP and comp_list in comps:
                    del comps[GROUP]

                elif comp_list in comps:
                    name = comp_list
                    comp_list = self.__format_component_lists(comps[comp_list])
                    components[name] = comp_list
                    element[COMPS].extend(comp_list)

            element[COMPS] = Components(element[COMPS])
            del element[DSD_COMPS]

        return element

    def __format_vtl(self, json_vtl: Dict[str, Any]) -> Dict[str, Any]:
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
    ) -> Dict[str, Any]:
        elements: Dict[str, Any] = {}

        json_elem[scheme] = add_list(json_elem[scheme])
        for element in json_elem[scheme]:
            element["items"] = []

            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            full_id = unique_id(
                element[AGENCY_ID], element[ID], element[VERSION]
            )
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
            if scheme == AGENCIES:
                self.agencies.update({e.id: e for e in items})
            if scheme == CS:
                self.concepts.update({e.id: e for e in items})
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            element = self.__format_vtl(element)
            # Dynamic creation with specific class
            elements[full_id] = STRUCTURES_MAPPING[scheme](**element)

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
        datastructures = {}

        json_element[item] = add_list(json_element[item])
        for element in json_element[item]:
            if URN.lower() in element and element[URN.lower()] is not None:
                full_id = parse_urn(element[URN.lower()]).__str__()
            else:
                full_id = unique_id(
                    element[AGENCY_ID], element[ID], element[VERSION]
                )
                full_id = f"{item}={full_id}"

            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            element = self.__format_urls(element)
            element = self.__format_agency(element)
            element = self.__format_validity(element)
            element = self.__format_components(element)

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
                ref_data = element[STR][REF]
                reference_str = f"{ref_data[CLASS]}={ref_data[AGENCY_ID]}:{ref_data[ID]}({ref_data[VERSION]})"
                if reference_str in self.datastructures:
                    element[STR] = self.datastructures[reference_str]
                else:
                    element[STR] = reference_str

            structure = {key.lower(): value for key, value in element.items()}
            if schema == DSDS:
                if COMPS in structure:
                    structure[COMPS] = Components(structure[COMPS])
                else:
                    structure[COMPS] = Components([])
                self.datastructures[full_id] = STRUCTURES_MAPPING[schema](**structure)
            datastructures[full_id] = STRUCTURES_MAPPING[schema](**structure)

        return datastructures

    def format_structures(self, json_meta: Dict[str, Any]) -> Dict[str, Any]:
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
        if CLS in json_meta:
            structures[CLS] = self.__format_scheme(json_meta[CLS], CL, CODE)
            self.codelists = structures[CLS]
        if CONCEPTS in json_meta:
            structures[CONCEPTS] = self.__format_scheme(
                json_meta[CONCEPTS], CS, CON
            )
        if DSDS in json_meta:
            structures[DSDS] = self.__format_schema(json_meta[DSDS], DSDS, DSD)
        if DFWS in json_meta:
            structures[DFWS] = self.__format_schema(json_meta[DFWS], DFWS, DFW)

        if TRANSFORMATIONS in json_meta:
            structures[TRANSFORMATIONS] = self.__format_scheme(
                json_meta[TRANSFORMATIONS], TRANS_SCHEME, TRANSFORMATION
            )
        # Reset global variables
        return structures
