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
from pysdmx.model.map import (
    MultiRepresentationMap,
    RepresentationMap,
    StructureMap,
)
from pysdmx.model.metadata import MetadataReport
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


class Header(Struct, repr_omit_defaults=True, kw_only=True):
    """Header for the SDMX messages.

    Represents the Header of an SDMX message, containing metadata about the
    message such as the sender, receiver, and other relevant information.

    Attributes:
        id: Unique identifier for the message. (default: generated UUID)
        test: Indicates if the message is a test message. (default: False)
        prepared: Timestamp when the message was prepared.
          (default: current UTC time)
        sender: Organisation that sent the message.
          (default: Organisation with id "ZZZ")
        receiver: Optional Organisation that received the message.
          (default: None)
        source: Optional source of the message. (default: None)
        dataset_action: Optional action for the dataset
          (only for SDMX Data messages). (default: None)
        structure: Dimension at observation mapping
          (dict with short URN as key and Dimension ID as value)
          (only for SDMX Data Messages)
          (Overridden by dimension_at_observation argument in writers).
          (default: None)
        dataset_id: DatasetID defined at SDMX-ML
          (only for SDMX-ML Data messages). (default: None)
    """

    id: str = str(uuid.uuid4())
    test: bool = False
    prepared: datetime = datetime.now(timezone.utc)
    sender: Organisation = Organisation(id="ZZZ")
    receiver: Optional[Organisation] = None
    source: Optional[str] = None
    dataset_action: Optional[ActionType] = None
    structure: Optional[Dict[str, str]] = None
    dataset_id: Optional[str] = None

    def __post_init__(self) -> None:
        """Header post-initialization."""
        if isinstance(self.sender, str):
            self.sender = Organisation(id=self.sender)

        if isinstance(self.receiver, str):
            self.receiver = Organisation(id=self.receiver)

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"


class StructureMessage(Struct, repr_omit_defaults=True, frozen=True):
    """Message class holds the content of an SDMX Structure Message.

    Attributes:
        header: The header of the SDMX message.
        structures: Sequence of MaintainableArtefact objects.
          They represent the contents of a Structure Message.
    """

    header: Optional[Header] = None
    structures: Optional[Sequence[MaintainableArtefact]] = None

    def __post_init__(self) -> None:
        """Checks if the content is valid."""
        if self.structures is not None:
            for obj_ in self.structures:
                if not isinstance(obj_, (MaintainableArtefact)):
                    raise Invalid(
                        f"Invalid structure: {type(obj_).__name__} ",
                        "Check the docs on structures.",
                    )

    def __str__(self) -> str:
        """Custom string representation with detailed structure counts."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            if attr in ["data", "structures"] and value:
                # Count occurrences of each class in structures
                class_counts: Dict[str, int] = {}
                for obj in value:
                    class_name = obj.__class__.__name__
                    class_counts[class_name] = (
                        class_counts.get(class_name, 0) + 1
                    )

                # Format the counts
                value = ", ".join(
                    f"{count} {class_name.lower()}"
                    for class_name, count in class_counts.items()
                )

            # Handle sequences and omit empty ones
            if (
                isinstance(value, Sequence)
                and not isinstance(value, str)
                and not value
            ):
                continue

            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # Omit empty sequences
            if isinstance(value, (list, tuple, set)) and not value:
                continue
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"

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
        """Returns the CategorySchemes."""
        return self.__get_elements(CategoryScheme)

    def get_value_lists(self) -> List[Codelist]:
        """Returns the Codelists."""
        return self.__get_enumerations(Codelist, True)

    def get_hierarchies(self) -> List[Hierarchy]:
        """Returns the HierarchyCodelists."""
        return self.__get_elements(Hierarchy)

    def get_hierarchy_associations(self) -> List[HierarchyAssociation]:
        """Returns the HierarchyAssociations."""
        return self.__get_elements(HierarchyAssociation)

    def get_data_provider_schemes(self) -> List[DataProviderScheme]:
        """Returns the DataProviderSchemes."""
        return self.__get_elements(DataProviderScheme)

    def get_provision_agreements(self) -> List[ProvisionAgreement]:
        """Returns the ProvisionAgreements."""
        return self.__get_elements(ProvisionAgreement)

    def get_structure_maps(self) -> List[StructureMap]:
        """Returns the StructureMaps."""
        return self.__get_elements(StructureMap)

    def get_representation_maps(
        self,
    ) -> List[Union[MultiRepresentationMap, RepresentationMap]]:
        """Returns the RepresentationMaps."""
        out = []
        out.extend(self.__get_elements(RepresentationMap))
        out.extend(self.__get_elements(MultiRepresentationMap))
        return out

    def get_categorisations(self) -> List[Categorisation]:
        """Returns the Categorisations."""
        return self.__get_elements(Categorisation)

    def get_custom_type_schemes(self) -> List[CustomTypeScheme]:
        """Returns the CustomType Schemes."""
        return self.__get_elements(CustomTypeScheme)

    def get_vtl_mapping_schemes(self) -> List[VtlMappingScheme]:
        """Returns the VTL Mapping Schemes."""
        return self.__get_elements(VtlMappingScheme)

    def get_name_personalisation_schemes(
        self,
    ) -> List[NamePersonalisationScheme]:
        """Returns the NamePersonalisationSchemes."""
        return self.__get_elements(NamePersonalisationScheme)


class MetadataMessage(Struct, frozen=True):
    """Message class holds the content of an SDMX Reference Metadata Message.

    Attributes:
        header: The header of the SDMX message.
        reports: Sequence of metadata reports.
    """

    header: Optional[Header] = None
    reports: Optional[Sequence[MetadataReport]] = None

    def get_reports(self) -> Sequence[MetadataReport]:
        """Returns the metadata reports."""
        if self.reports:
            return self.reports
        else:
            raise NotFound("No metadata reports werefound in the message.")


class Message(StructureMessage, frozen=True):
    """Message class holds the content of SDMX Message.

    Attributes:
        header: The header of the SDMX message.
        structures: Sequence of MaintainableArtefact objects.
        data: Sequence of Dataset objects. They represent the contents of a
           SDMX Data Message in any format.
        submission: Sequence of SubmissionResult objects. They represent the
              contents of a SDMX Submission Message.
    """

    data: Optional[Sequence[Dataset]] = None
    submission: Optional[Sequence[SubmissionResult]] = None

    def __post_init__(self) -> None:
        """Checks if the content is valid."""
        super().__post_init__()
        if self.data is not None:
            for data_value in self.data:
                if not isinstance(data_value, Dataset):
                    raise Invalid(
                        f"Invalid data type: "
                        f"{type(data_value).__name__} "
                        f"for Data Message, requires a Dataset object.",
                        "Check the docs for the proper structure on data.",
                    )

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
