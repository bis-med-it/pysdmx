"""Message module.

This module contains the enumeration for the different types of messages that
can be written. It also contains the Header and Message classes that are used
to create the SDMX messages.

Classes:
    Header: Header for the SDMX messages.
    ActionType: Enumeration for the different types of actions that can be
        written.
    Message: Class that holds the content of the SDMX message.
    SubmissionResult: Class that represents the result of a submission.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
import uuid

from msgspec import Struct

from pysdmx.errors import Invalid, NotFound
from pysdmx.model import Codelist, ConceptScheme
from pysdmx.model.__base import ItemScheme


class ActionType(Enum):
    """ActionType enumeration.

    Enumeration that withholds the Action type for writing purposes.
    """

    Append = "append"
    Replace = "replace"
    Delete = "delete"
    Information = "information"


class Header(Struct, frozen=True, kw_only=True):
    """Header for the SDMX messages."""

    id: str = str(uuid.uuid4())
    test: bool = True
    prepared: datetime = datetime.now(timezone.utc)
    sender: str = "ZZZ"
    receiver: Optional[str] = None
    source: Optional[str] = None
    dataset_action: Optional[ActionType] = None


ORGS = "OrganisationSchemes"
CLS = "Codelists"
CONCEPTS = "Concepts"

MSG_CONTENT_PKG = {
    ORGS: ItemScheme,
    CLS: Codelist,
    CONCEPTS: ConceptScheme,
}


class Message(Struct, frozen=True):
    """Message class holds the content of SDMX Message.

    Attributes:
        content (Dict[str, Any]): Content of the message. The keys are the
            content type (e.g. ``OrganisationSchemes``, ``Codelists``, etc.),
            and the values are the content objects (e.g. ``ItemScheme``,
            ``Codelist``, etc.).
    """

    content: Dict[str, Any]

    def __post_init__(self) -> None:
        """Checks if the content is valid."""
        for content_key, content_value in self.content.items():
            if content_key not in MSG_CONTENT_PKG:
                raise Invalid(
                    f"Invalid content type: {content_key}",
                    "Check the docs for the proper structure on content.",
                )

            for obj_ in content_value.values():
                if not isinstance(obj_, MSG_CONTENT_PKG[content_key]):
                    raise Invalid(
                        f"Invalid content value type: {type(obj_).__name__} "
                        f"for {content_key}",
                        "Check the docs for the proper "
                        "structure on content.",
                    )

    def __get_elements(self, type_: str) -> Dict[str, Any]:
        """Returns the elements from content."""
        if type_ in self.content:
            return self.content[type_]
        raise NotFound(
            f"No {type_} found in content",
            f"Could not find any {type_} in content.",
        )

    def __get_element_by_uid(self, type_: str, unique_id: str) -> Any:
        """Returns a specific element from content."""
        if type_ not in self.content:
            raise NotFound(
                f"No {type_} found.",
                f"Could not find any {type_} in content.",
            )

        if unique_id in self.content[type_]:
            return self.content[type_][unique_id]

        raise NotFound(
            f"No {type_} with id {unique_id} found in content",
            "Could not find the requested element.",
        )

    def get_organisation_schemes(self) -> Dict[str, ItemScheme]:
        """Returns the OrganisationScheme."""
        return self.__get_elements(ORGS)

    def get_codelists(self) -> Dict[str, Codelist]:
        """Returns the Codelist."""
        return self.__get_elements(CLS)

    def get_concept_schemes(self) -> Dict[str, ConceptScheme]:
        """Returns the Concept."""
        return self.__get_elements(CONCEPTS)

    def get_organisation_scheme_by_uid(self, unique_id: str) -> ItemScheme:
        """Returns a specific OrganisationScheme."""
        return self.__get_element_by_uid(ORGS, unique_id)

    def get_codelist_by_uid(self, unique_id: str) -> Codelist:
        """Returns a specific Codelist."""
        return self.__get_element_by_uid(CLS, unique_id)

    def get_concept_scheme_by_uid(self, unique_id: str) -> ConceptScheme:
        """Returns a specific Concept."""
        return self.__get_element_by_uid(CONCEPTS, unique_id)


class SubmissionResult(Struct, frozen=True):
    """A class to represent a Submission Result."""

    action: str
    short_urn: str
    status: str

    def __str__(self) -> str:
        """Return a string representation of the SubmissionResult."""
        return (
            f"<Submission Result - "
            f"Action: {self.action} - "
            f"Short URN: {self.short_urn} - "
            f"Status: {self.status}>"
        )
