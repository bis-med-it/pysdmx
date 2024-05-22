"""Parsers for reading metadata."""

from typing import Any, Dict

from msgspec import Struct

from pysdmx.io.xml.sdmx21.reader.__utils import (
    add_list,
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
    EMAIL,
    EMAILS,
    FACETS,
    FacetType,
    FAX,
    FAXES,
    ID,
    missing_rep,
    NAME,
    PAR_ID,
    PAR_VER,
    ROLE,
    SER_URL,
    SER_URL_LOW,
    STR_URL,
    STR_URL_LOW,
    TELEPHONE,
    TELEPHONES,
    TEXT,
    TEXT_TYPE,
    TEXT_TYPE_LOW,
    TITLE,
    TYPE,
    unique_id,
    URI,
    URIS,
    URL,
    VERSION,
    XMLNS,
)
from pysdmx.model import Code, Codelist, Concept, ConceptScheme, Facets
from pysdmx.model.__base import Agency, Annotation, Contact, Item, ItemScheme
from pysdmx.model.message import CONCEPTS, ORGS

SCHEMES_CLASSES = {CL: Codelist, AGENCIES: ItemScheme, CS: ConceptScheme}
ITEMS_CLASSES = {AGENCY: Agency, CODE: Code, CON: Concept}


class StructureParser(Struct):
    """StructureParser class for SDMX-ML 2.1."""

    agencies: Dict[str, Any]
    codelists: Dict[str, Any]
    concepts: Dict[str, Any]
    datastructures: Dict[str, Any]
    dataflows: Dict[str, Any]

    @staticmethod
    def __format_contact(json_contact: Dict[str, Any]) -> Contact:
        """Creates a Contact object from a json_contact.

        Args:
            json_contact: The element to create the Contact object from

        Returns:
            Contact object created from the json_contact
        """
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
                json_contact[v] = add_list(json_contact.pop(k))

        return Contact(**json_contact)

    @staticmethod
    def __format_annotations(item_elem: Any) -> Dict[str, Any]:
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
        if ANNOTATION not in ann:
            item_elem[ANNOTATIONS.lower()] = []
            del item_elem[ANNOTATIONS]
            return item_elem

        ann[ANNOTATION] = add_list(ann[ANNOTATION])
        for e in ann[ANNOTATION]:
            if ANNOTATION_TITLE in e:
                e[TITLE] = e.pop(ANNOTATION_TITLE)
            if ANNOTATION_TYPE in e:
                e[TYPE] = e.pop(ANNOTATION_TYPE)
            if ANNOTATION_TEXT in e:
                e[TEXT] = e[ANNOTATION_TEXT]
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
        for e in node:
            if e in element:
                element[e.lower()] = element[e]
                del element[e]
        return element

    @staticmethod
    def __format_facets(json_fac: Dict[str, Any]) -> Dict[str, Any]:
        """Formats the facets in the json_fac.

        Args:
            json_fac: The element with the facets to be formatted

        Returns:
            facets formatted
        """
        fac: Dict[str, Any] = {FACETS: []}
        if json_fac is None:
            return fac
        if TEXT_TYPE in json_fac:
            fac[TEXT_TYPE_LOW] = json_fac.pop(TEXT_TYPE)
        for key, _value in json_fac.items():
            if key in FacetType:
                facet_kwargs = {
                    k: v for k, v in json_fac.items() if k in FacetType
                }
                fac[FACETS].append(Facets(**facet_kwargs))

        return fac

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
        element[AGENCY] = self.agencies.get(element[AGENCY_ID])
        del element[AGENCY_ID]
        return element

    def __format_con_id(self, json_ref: Dict[str, Any]) -> Dict[str, Any]:
        """Formats the Concept key on element to have a trailing underscore.

        Args:
            json_ref: The element to be formatted

        Returns:
            json_ref with Concept key formatted
        """
        rep = {}
        full_cs_id = unique_id(
            json_ref[AGENCY_ID], json_ref[PAR_ID], json_ref[PAR_VER]
        )
        if full_cs_id in self.concepts:
            if json_ref[ID] in self.concepts[full_cs_id]["items"]:
                rep[CON] = self.concepts[full_cs_id]["items"][json_ref[ID]]
                core_rep = self.concepts[full_cs_id]["items"][json_ref[ID]][
                    "core_representation"
                ]
                if core_rep is not None:
                    cl = core_rep["codelist"]
                    if cl is not None:
                        rep[CL.lower()] = cl
            elif json_ref[ID] not in missing_rep["CON"]:
                missing_rep["CON"].append(json_ref[ID])

        elif full_cs_id not in missing_rep["CS"]:
            missing_rep["CS"].append(full_cs_id)

        return rep

    def __format_orgs(self, json_orgs: Dict[str, Any]) -> Dict[str, Any]:
        orgs: Dict[str, Any] = {}
        if AGENCIES in json_orgs:
            if len(json_orgs) == 1 and isinstance(json_orgs[AGENCIES], dict):
                ag_sch = self.__format_scheme(json_orgs, AGENCIES, AGENCY)
                return ag_sch
            for e in json_orgs[AGENCIES]:
                ag_sch = self.__format_scheme(e, AGENCIES, AGENCY)
                orgs = {**orgs, **ag_sch}
        return orgs

    def __format_item(
        self, item_json_info: Dict[str, Any], item_name_class: str
    ) -> Item:
        if XMLNS in item_json_info:
            del item_json_info[XMLNS]

        item_json_info = self.__format_annotations(item_json_info)
        item_json_info = self.__format_name_description(item_json_info)

        if CONTACT in item_json_info and item_name_class == AGENCY:
            item_json_info[CONTACT] = add_list(item_json_info[CONTACT])
            contacts = []
            for e in item_json_info[CONTACT]:
                contacts.append(self.__format_contact(e))
            item_json_info[CONTACT.lower() + "s"] = contacts
            del item_json_info[CONTACT]

        # if CORE_REP in item_json_info and item_name_class == CON:
        #     item_json_info[CORE_REP_LOW] = format_representation(
        #         item_json_info[CORE_REP])
        #     del item_json_info[CORE_REP]

        return ITEMS_CLASSES[item_name_class](**item_json_info)

    def __format_scheme(
        self, json_elem: Dict[str, Any], scheme: str, item: str
    ) -> Dict[str, Any]:
        elements: Dict[str, Any] = {}
        if scheme not in json_elem:
            return elements

        json_elem[scheme] = add_list(json_elem[scheme])
        for element in json_elem[scheme]:

            if XMLNS in element:
                del element[XMLNS]

            element = self.__format_annotations(element)
            element = self.__format_name_description(element)
            full_id = unique_id(
                element[AGENCY_ID], element[ID], element[VERSION]
            )
            element = self.__format_urls(element)
            element = self.__format_agency(element)
            if item in element:
                element[item] = add_list(element[item])
                items = []
                for item_elem in element[item]:
                    # Dynamic
                    items.append(self.__format_item(item_elem, item))
                del element[item]
                element["items"] = items
                if scheme == AGENCIES:
                    self.agencies.update({e.id: e for e in items})
            else:
                element["items"] = []
            # Dynamic creation with specific class
            elements[full_id] = SCHEMES_CLASSES[scheme](**element)

        return elements

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
        if CONCEPTS in json_meta:
            structures[CONCEPTS] = self.__format_scheme(
                json_meta[CONCEPTS], CS, CON
            )
        # Reset global variables
        return structures
