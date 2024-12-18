"""Parsers for reading metadata."""

from typing import Any, Dict

from msgspec import Struct

from pysdmx.io.xml.sdmx21.__parsing_config import CORE_REP, URN
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
    STR_URL,
    STR_URL_LOW,
    TELEPHONE,
    TELEPHONES,
    TEXT,
    TEXT_TYPE,
    TITLE,
    TYPE,
    unique_id,
    URI,
    URIS,
    URL,
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
from pysdmx.model.message import CONCEPTS, ORGS
from pysdmx.util import find_by_urn

SCHEMES_CLASSES = {CL: Codelist, AGENCIES: ItemScheme, CS: ConceptScheme}
ITEMS_CLASSES = {AGENCY: Agency, CODE: Code, CON: Concept}


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
        for key, _value in json_fac.items():
            if key == TEXT_TYPE and json_fac[TEXT_TYPE] in list(DataType):
                json_obj["dtype"] = DataType(json_fac[TEXT_TYPE])

            if key in FacetType:
                facet_kwargs = {
                    FacetType[k]: v
                    for k, v in json_fac.items()
                    if k in FacetType
                }
                json_obj[FACETS] = Facets(**facet_kwargs)

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

    def __format_representation(
        self, json_rep: Dict[str, Any], json_obj: Dict[str, Any]
    ) -> None:
        """Formats the representation in the json_rep."""
        if "TextFormat" in json_rep:
            self.__format_facets(json_rep["TextFormat"], json_obj)

        if (
            "Enumeration" in json_rep
            and URN in json_rep["Enumeration"]
            and len(self.codelists) > 0
        ):
            codelist = find_by_urn(
                list(self.codelists.values()),
                json_rep["Enumeration"][URN],
            )
            json_obj["codes"] = codelist.codes

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
                element[IS_EXTERNAL_REF_LOW] = element.pop(IS_EXTERNAL_REF)
            if IS_FINAL in element:
                element[IS_FINAL_LOW] = element.pop(IS_FINAL)
            if IS_PARTIAL in element:
                element[IS_PARTIAL_LOW] = element.pop(IS_PARTIAL)
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
            self.codelists = structures[CLS]
        if CONCEPTS in json_meta:
            structures[CONCEPTS] = self.__format_scheme(
                json_meta[CONCEPTS], CS, CON
            )
        # Reset global variables
        return structures
