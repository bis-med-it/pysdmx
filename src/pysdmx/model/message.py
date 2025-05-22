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
from typing import Any, Dict, List, Optional, Sequence, Type, Union

from msgspec import Struct

from pysdmx.errors import Invalid, NotFound
from pysdmx.model.__base import ItemScheme, MaintainableArtefact, Organisation
from pysdmx.model.category import Categorisation, CategoryScheme
from pysdmx.model.code import Codelist, Hierarchy, HierarchyAssociation
from pysdmx.model.concept import ConceptScheme
from pysdmx.model.dataflow import (
    Dataflow,
    DataStructureDefinition,
    ProvisionAgreement,
)
from pysdmx.model.dataset import ActionType, Dataset
from pysdmx.model.map import RepresentationMap, StructureMap
from pysdmx.model.organisation import AgencyScheme, DataProviderScheme
from pysdmx.model.submission import SubmissionResult
from pysdmx.model.vtl import (
    CustomTypeScheme,
    NamePersonalisationScheme,
    RulesetScheme,
    TransformationScheme,
    UserDefinedOperatorScheme,
    VtlMappingScheme,
)


class Header(Struct, kw_only=True):
    """Header for the SDMX messages."""

    id: str = str(uuid.uuid4())
    test: bool = False
    prepared: datetime = datetime.now(timezone.utc)
    sender: Organisation = Organisation(id="ZZZ")
    receiver: Optional[Organisation] = None
    source: Optional[str] = None
    dataset_action: Optional[ActionType] = None
    structure: Optional[Dict[str, str]] = None
    dataset_id: Optional[str] = None


class Message(Struct, frozen=True):
    """Message class holds the content of SDMX Message.

    Attributes:
        structures: Sequence of structure objects (ItemScheme, Schema).
           They represent the contents of a Structure Message.
        data: Sequence of Dataset objects. They represent the contents of a
           SDMX Data Message in any format.
        submission: Sequence of SubmissionResult objects. They represent the
              contents of a SDMX Submission Message.
    """

    header: Optional[Header] = None
    structures: Optional[Sequence[MaintainableArtefact]] = None
    data: Optional[Sequence[Dataset]] = None
    submission: Optional[Sequence[SubmissionResult]] = None

    def __post_init__(self) -> None:
        """Checks if the content is valid."""
        if self.structures is not None:
            for obj_ in self.structures:
                if not isinstance(obj_, (MaintainableArtefact)):
                    raise Invalid(
                        f"Invalid structure: " f"{type(obj_).__name__} ",
                        "Check the docs on structures.",
                    )
        if self.data is not None:
            for data_value in self.data:
                if not isinstance(data_value, Dataset):
                    raise Invalid(
                        f"Invalid data type: "
                        f"{type(data_value).__name__} "
                        f"for Data Message, requires a Dataset object.",
                        "Check the docs for the proper structure on data.",
                    )

    def __get_elements(self, type_: Type[Any]) -> List[Any]:
        """Returns a list of elements of a specific type."""
        if self.structures is None:
            raise NotFound(
                f"No {type_.__name__} found in message.",
            )
        structures = []
        for element in self.structures:
            if isinstance(element, type_):
                structures.append(element)
        return structures

    def __get_enumerations(
        self, type_: Type[Any], is_vl: bool = False
    ) -> List[Any]:
        """Returns a list of elements of a specific type."""
        enums = self.__get_elements(type_)
        t = "valuelist" if is_vl else "codelist"
        return [e for e in enums if e.sdmx_type == t]

    def __get_single_structure(
        self,
        type_: Type[Union[ItemScheme, DataStructureDefinition, Dataflow]],
        short_urn: str,
    ) -> Any:
        """Returns a specific element from content."""
        if self.structures is None:
            raise NotFound(
                f"No {type_.__name__} found in message.",
                "Could not find any Structures in this message.",
            )
        for structure in self.structures:
            if structure.short_urn == short_urn:
                return structure

        raise NotFound(
            f"No {type_.__name__} with Short URN {short_urn} found in message",
            "Could not find the requested element.",
        )

    def get_agency_schemes(self) -> List[AgencyScheme]:
        """Returns the AgencySchemes."""
        return self.__get_elements(AgencyScheme)

    def get_codelists(self) -> List[Codelist]:
        """Returns the Codelists."""
        return self.__get_enumerations(Codelist, False)

    def get_concept_schemes(self) -> List[ConceptScheme]:
        """Returns the Concept Schemes."""
        return self.__get_elements(ConceptScheme)

    def get_data_structure_definitions(
        self,
    ) -> List[DataStructureDefinition]:
        """Returns the DataStructureDefinitions."""
        return self.__get_elements(DataStructureDefinition)

    def get_dataflows(self) -> List[Dataflow]:
        """Returns the Dataflows."""
        return self.__get_elements(Dataflow)

    def get_organisation_scheme(self, short_urn: str) -> AgencyScheme:
        """Returns a specific OrganisationScheme."""
        return self.__get_single_structure(AgencyScheme, short_urn)

    def get_codelist(self, short_urn: str) -> Codelist:
        """Returns a specific Codelist."""
        return self.__get_single_structure(Codelist, short_urn)

    def get_concept_scheme(self, short_urn: str) -> ConceptScheme:
        """Returns a specific Concept Scheme."""
        return self.__get_single_structure(ConceptScheme, short_urn)

    def get_data_structure_definition(
        self, short_urn: str
    ) -> DataStructureDefinition:
        """Returns a specific DataStructureDefinition."""
        return self.__get_single_structure(DataStructureDefinition, short_urn)

    def get_dataflow(self, short_urn: str) -> Dataflow:
        """Returns a specific Dataflow."""
        return self.__get_single_structure(Dataflow, short_urn)

    def get_datasets(self) -> Sequence[Dataset]:
        """Returns the Datasets."""
        if self.data is not None:
            return self.data
        raise NotFound(
            "No Datasets found in data.",
            "Could not find any Datasets in content.",
        )

    def get_dataset(self, short_urn: str) -> Dataset:
        """Returns a specific Dataset."""
        if self.data is not None:
            for dataset in self.data:
                if dataset.short_urn == short_urn:
                    return dataset
        raise NotFound(
            f"No Dataset with Short URN {short_urn} found in data.",
            "Could not find the requested Dataset.",
        )

    def get_transformation_schemes(self) -> List[TransformationScheme]:
        """Returns the TransformationSchemes."""
        return self.__get_elements(TransformationScheme)

    def get_user_defined_operator_schemes(
        self,
    ) -> List[UserDefinedOperatorScheme]:
        """Returns the UserDefinedOperatorSchemes."""
        return self.__get_elements(UserDefinedOperatorScheme)

    def get_ruleset_schemes(self) -> List[RulesetScheme]:
        """Returns the RulesetSchemes."""
        return self.__get_elements(RulesetScheme)

    def get_category_schemes(self) -> List[CategoryScheme]:
        """Returns the Codelists."""
        return self.__get_elements(CategoryScheme)

    def get_value_lists(self) -> List[Codelist]:
        """Returns the Codelists."""
        return self.__get_enumerations(Codelist, True)

    def get_hierarchies(self) -> List[Hierarchy]:
        """Returns the Codelists."""
        return self.__get_elements(Hierarchy)

    def get_hierarchy_associations(self) -> List[HierarchyAssociation]:
        """Returns the Codelists."""
        return self.__get_elements(HierarchyAssociation)

    def get_data_provider_schemes(self) -> List[DataProviderScheme]:
        """Returns the Codelists."""
        return self.__get_elements(DataProviderScheme)

    def get_provision_agreements(self) -> List[ProvisionAgreement]:
        """Returns the Codelists."""
        return self.__get_elements(ProvisionAgreement)

    def get_structure_maps(self) -> List[StructureMap]:
        """Returns the Codelists."""
        return self.__get_elements(StructureMap)

    def get_representation_maps(self) -> List[RepresentationMap]:
        """Returns the Codelists."""
        return self.__get_elements(RepresentationMap)

    def get_categorisations(self) -> List[Categorisation]:
        """Returns the Codelists."""
        return self.__get_elements(Categorisation)

    def get_custom_type_schemes(self) -> List[CustomTypeScheme]:
        """Returns the Codelists."""
        return self.__get_elements(CustomTypeScheme)

    def get_vtl_mapping_schemes(self) -> List[VtlMappingScheme]:
        """Returns the Codelists."""
        return self.__get_elements(VtlMappingScheme)

    def get_name_personalisation_schemes(
        self,
    ) -> List[NamePersonalisationScheme]:
        """Returns the Codelists."""
        return self.__get_elements(NamePersonalisationScheme)
