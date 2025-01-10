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

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.errors import Invalid, NotFound
from pysdmx.model.__base import ItemScheme
from pysdmx.model.code import Codelist
from pysdmx.model.concept import ConceptScheme
from pysdmx.model.dataflow import Dataflow, DataStructureDefinition
from pysdmx.model.dataset import ActionType, Dataset


class Header(Struct, kw_only=True):
    """Header for the SDMX messages."""

    id: str = str(uuid.uuid4())
    test: bool = True
    prepared: datetime = datetime.now(timezone.utc)
    sender: str = "ZZZ"
    receiver: Optional[str] = None
    source: Optional[str] = None
    dataset_action: Optional[ActionType] = None
    structure: Optional[Dict[str, str]] = None


# Prevent circular import by defining the words in the message module
ORGS = "OrganisationSchemes"
CLS = "Codelists"
CONCEPTS = "Concepts"
DSDS = "DataStructures"
DFWS = "Dataflows"

MSG_CONTENT_PKG = {
    ORGS: ItemScheme,
    CLS: Codelist,
    CONCEPTS: ConceptScheme,
    DSDS: DataStructureDefinition,
    DFWS: Dataflow,
}


class Message(Struct, frozen=True):
    """Message class holds the content of SDMX Message.

    Attributes:
        structures (dict): Content of the Structure Message. The keys are the
            content type (e.g. ``OrganisationSchemes``, ``Codelists``, etc.),
            and the values are the content objects (e.g. ``ItemScheme``,
            ``Codelist``, etc.).
        data (dict): Content of the Data Message.
             The keys are the dataset short URNs, and the values
             are the Dataset objects.
    """

    structures: Optional[
        Dict[
            str,
            Dict[
                str,
                Union[
                    ItemScheme,
                    Codelist,
                    ConceptScheme,
                    DataStructureDefinition,
                    Dataflow,
                ],
            ],
        ]
    ] = None
    data: Optional[Dict[str, Dataset]] = None

    def __post_init__(self) -> None:
        """Checks if the content is valid."""
        if self.structures is not None:
            for content_key, content_value in self.structures.items():
                if content_key not in MSG_CONTENT_PKG:
                    raise Invalid(
                        f"Invalid content type: {content_key}",
                        "Check the docs for the proper "
                        "structure on structures.",
                    )

                for obj_ in content_value.values():
                    if not isinstance(obj_, MSG_CONTENT_PKG[content_key]):
                        raise Invalid(
                            f"Invalid content value type: "
                            f"{type(obj_).__name__} "
                            f"for {content_key}",
                            "Check the docs for the proper "
                            "structure on structures.",
                        )
        if self.data is not None:
            for data_value in self.data.values():
                if not isinstance(data_value, Dataset):
                    raise Invalid(
                        f"Invalid data type: "
                        f"{type(data_value).__name__} "
                        f"for Data Message, requires a Dataset object.",
                        "Check the docs for the proper structure on data.",
                    )

    def __get_elements(self, type_: str) -> Dict[str, Any]:
        """Returns the elements from content."""
        if self.structures is not None and type_ in self.structures:
            return self.structures[type_]
        raise NotFound(
            f"No {type_} found in content",
            f"Could not find any {type_} in content.",
        )

    def __get_single_structure(self, type_: str, short_urn: str) -> Any:
        """Returns a specific element from content."""
        if self.structures is not None and type_ not in self.structures:
            raise NotFound(
                f"No {type_} found.",
                f"Could not find any {type_} in content.",
            )

        if self.structures is not None and short_urn in self.structures[type_]:
            return self.structures[type_][short_urn]

        raise NotFound(
            f"No {type_} with Short URN {short_urn} found in content",
            "Could not find the requested element.",
        )

    def get_organisation_schemes(self) -> Dict[str, ItemScheme]:
        """Returns the OrganisationSchemes."""
        return self.__get_elements(ORGS)

    def get_codelists(self) -> Dict[str, Codelist]:
        """Returns the Codelists."""
        return self.__get_elements(CLS)

    def get_concept_schemes(self) -> Dict[str, ConceptScheme]:
        """Returns the Concept Schemes."""
        return self.__get_elements(CONCEPTS)

    def get_data_structure_definitions(
        self,
    ) -> Dict[str, DataStructureDefinition]:
        """Returns the DataStructureDefinitions."""
        return self.__get_elements(DSDS)

    def get_dataflows(self) -> Dict[str, Dataflow]:
        """Returns the Dataflows."""
        return self.__get_elements(DFWS)

    def get_organisation_scheme(self, short_urn: str) -> ItemScheme:
        """Returns a specific OrganisationScheme."""
        return self.__get_single_structure(ORGS, short_urn)

    def get_codelist(self, short_urn: str) -> Codelist:
        """Returns a specific Codelist."""
        return self.__get_single_structure(CLS, short_urn)

    def get_concept_scheme(self, short_urn: str) -> ConceptScheme:
        """Returns a specific Concept."""
        return self.__get_single_structure(CONCEPTS, short_urn)

    def get_data_structure_definition(
        self, short_urn: str
    ) -> DataStructureDefinition:
        """Returns a specific DataStructureDefinition."""
        return self.__get_single_structure(DSDS, short_urn)

    def get_dataflow(self, short_urn: str) -> Dataflow:
        """Returns a specific Dataflow."""
        return self.__get_single_structure(DFWS, short_urn)

    def get_datasets(self) -> Sequence[Dataset]:
        """Returns the Datasets."""
        if self.data is not None:
            return list(self.data.values())
        raise NotFound(
            "No Datasets found in content",
            "Could not find any Datasets in content.",
        )

    def get_dataset(self, short_urn: str) -> Dataset:
        """Returns a specific Dataset."""
        if self.data is not None:
            for dataset in self.data.values():
                if dataset.short_urn == short_urn:
                    return dataset
        raise NotFound(
            f"No Dataset with Short URN {short_urn} found in content",
            "Could not find the requested Dataset.",
        )
