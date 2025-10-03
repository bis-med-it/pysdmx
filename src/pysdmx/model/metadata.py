"""Model for SDMX Reference Metadata.

Reference metadata are quite generic (and therefore powerful) in SDMX.
Though they are typically used to provide additional information about
statistical data, such as information about the general methodological
and quality aspects of the statistical production process, they can also
be used to drive process steps such as validation or mapping, for
example by providing configuration details in a metadata report.
"""

from collections import defaultdict
from typing import Any, Dict, Iterator, List, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.errors import Invalid
from pysdmx.model.__base import (
    Annotation,
    IdentifiableArtefact,
    ItemReference,
    MaintainableArtefact,
    Reference,
)
from pysdmx.model.code import Codelist, Hierarchy
from pysdmx.model.concept import Concept, DataType, Facets
from pysdmx.model.dataflow import ArrayBoundaries
from pysdmx.model.dataset import ActionType


class MetadataComponent(
    IdentifiableArtefact, frozen=True, omit_defaults=True, kw_only=True
):
    """A component defines the expected structure of a metadata attribute.

    The metadata component takes its semantic, and in some cases it
    representation, from its concept identity. A metadata component
    may be coded (via the local representation), uncoded (via the text
    format), or take no value. In addition to this value, the metadata
    component may also specify subordinate metadata components.

    If a metadata component only serves the purpose of containing
    subordinate metadata components, then the is_presentational attribute
    should be set to True. Otherwise, it is assumed to also take a value.

    If the metadata component does take a value, and a representation is
    not defined, it will be inherited from the concept it takes its
    semantic from. The optional id on the metadata component uniquely
    identifies it within the metadata structured definition.

    If this id is not supplied, its value is assumed to be that of the
    concept referenced from the concept identity. Note that a metadata
    component (as identified by the id attribute) definition must be
    unique across the entire metadata structure definition.

    Attributes:
        id: The identifier of the component.
        is_presentational: Whether the component is for presentation
            purposes only (e.g. a section header), or may contain a
            value.
        concept: The concept giving its identity to the component.
        local_dtype: The component's local data type (string, number, etc.).
        local_facets: Additional local details such as the component's minimum
            length.
        local_codes: The expected local values for the component (e.g. currency
            codes).
        array_def: Any additional constraints for array types.
        local_enum_ref: The URN of the enumeration (codelist or valuelist) from
            which the local codes are taken.
    """

    is_presentational: bool = False
    concept: Union[Concept, ItemReference]
    local_dtype: Optional[DataType] = None
    local_facets: Optional[Facets] = None
    local_codes: Union[Codelist, Hierarchy, None] = None
    array_def: Optional[ArrayBoundaries] = None
    local_enum_ref: Optional[str] = None
    components: Sequence["MetadataComponent"] = ()

    @property
    def dtype(self) -> DataType:
        """Returns the component data type.

        This will return the local data type (if any) or
        the data type of the referenced concept (if any).
        In case neither are set, the data type will default
        to string.

        Returns:
            The component data type (local, core or default).
        """
        if self.local_dtype:
            return self.local_dtype
        elif isinstance(self.concept, Concept) and self.concept.dtype:
            return self.concept.dtype
        else:
            return DataType.STRING

    @property
    def facets(self) -> Optional[Facets]:
        """Returns the component facets.

        This will return the local facets (if any) or
        the facets of the referenced concept (if any), or
        None in case neither are set.

        Returns:
            The component facets (local or core).
        """
        if self.local_facets:
            return self.local_facets
        elif isinstance(self.concept, Concept) and self.concept.facets:
            return self.concept.facets
        else:
            return None

    @property
    def enumeration(self) -> Union[Codelist, Hierarchy, None]:
        """Returns the list of valid codes for the component.

        This will return the local codes (if any) or
        the codes of the referenced concept (if any), or
        None in case neither are set.

        Returns:
            The component codes (local or core).
        """
        if self.local_codes:
            return self.local_codes
        elif isinstance(self.concept, Concept) and self.concept.codes:
            return self.concept.codes
        else:
            return None

    @property
    def enum_ref(self) -> Optional[str]:
        """Returns the URN of the enumeration from which the codes are taken.

        Returns:
            The URN of the enumeration from which the codes are taken.
        """
        if self.local_enum_ref:
            return self.local_enum_ref
        elif isinstance(self.concept, Concept) and self.concept.enum_ref:
            return self.concept.enum_ref
        else:
            return None

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class MetadataStructure(
    MaintainableArtefact, frozen=True, omit_defaults=True, kw_only=True
):
    """A metadata structure definition, i.e. a collection of metadata concepts.

    Attributes:
        id: The identifier for the MSD.
        name: The MSD name (e.g. "Frequency codelist").
        agency: The maintainer of the MSD (e.g. SDMX).
        description: Additional descriptive information about the MSD.
        version: The MSD version (e.g. 1.0.1)
        components: The MSD components, i.e. the collection of metadata
            concepts.
    """

    components: Sequence[MetadataComponent] = ()

    def __iter__(self) -> Iterator[MetadataComponent]:
        """Return an iterator over the list of components."""
        yield from self.components

    def __len__(self) -> int:
        """Return the number of components in the MSD."""
        return self.__get_count(self.components)

    def __getitem__(self, id_: str) -> Optional[MetadataComponent]:
        """Return the component identified by the given ID."""
        return self.__extract_cat(self.components, id_)

    def __contains__(self, id_: str) -> bool:
        """Whether there is a component with the supplied ID in the MSD."""
        return bool(self.__getitem__(id_))

    def __get_count(self, comps: Sequence[MetadataComponent]) -> int:
        """Return the number of components at any levels."""
        count = len(comps)
        for comp in comps:
            if comp.components:
                count += self.__get_count(comp.components)
        return count

    def __extract_cat(
        self, comps: Sequence[MetadataComponent], id_: str
    ) -> Optional[MetadataComponent]:
        if "." in id_:
            ids = id_.split(".")
            out = list(filter(lambda cat: cat.id == ids[0], comps))
            if out:
                pkey = ".".join(ids[1:])
                return self.__extract_cat(out[0].components, pkey)
        else:
            out = list(filter(lambda cat: cat.id == id_, comps))
            if out:
                return out[0]
        return None

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # str is taken as a Sequence, so we need to check it's not a str
            if isinstance(value, Sequence) and not isinstance(value, str):
                # Handle empty lists
                if not value:
                    continue
                class_name = value[0].__class__.__name__
                class_name = (
                    class_name.lower() + "s"
                    if attr != "components"
                    else "components"
                )
                value = f"{len(value)} {class_name}"

            processed_output.append(f"{attr}: {value}")
        return f"{', '.join(processed_output)}"


class Metadataflow(
    MaintainableArtefact,
    frozen=True,
    omit_defaults=True,
    tag=True,
    kw_only=True,
):
    """A flow of reference metadata that metadata providers will provide.

    Attributes:
        structure: The MSD describing the structure of all reference
            metadata reports for this metadataflow.
        targets: Identifiable structures to which the reference metadata
            reports described by the referenced MSD should be restricted to.
            For example, to indicate that the reports can be related to
            dataflows only, the following can be used:
            urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=*:*(*)
    """

    structure: Optional[Union[MetadataStructure, str]]
    targets: Union[Sequence[str], Sequence[Reference]]


class MetadataProvisionAgreement(
    MaintainableArtefact, frozen=True, omit_defaults=True, kw_only=True
):
    """Link between a metadata provider and metadataflow."""

    metadataflow: str
    metadata_provider: str


class MetadataAttribute(
    Struct, frozen=True, omit_defaults=True, repr_omit_defaults=True
):
    """An entry in a metadata report.

    An component is iterable, as it may contain other attributes.

    Attributes:
        id: The identifier of the attribute (e.g. "License").
        value: The attribute value (e.g. "BSD-2-Clause").
        attributes: The list of "children" attributes (i.e. attributes
            can be nested).
    """

    id: str
    value: Optional[Any] = None
    attributes: Sequence["MetadataAttribute"] = ()
    annotations: Sequence[Annotation] = ()
    format: Optional[Facets] = None

    def __iter__(self) -> Iterator["MetadataAttribute"]:
        """Return an iterator over the list of attributes."""
        yield from self.attributes

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # str is taken as a Sequence, so we need to check it's not a str
            if isinstance(value, Sequence) and not isinstance(value, str):
                # Handle non-empty lists
                if not value:
                    continue
                class_name = value[0].__class__.__name__
                value = f"{len(value)} {class_name.lower()}s"

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


class MetadataReport(MaintainableArtefact, frozen=True, omit_defaults=True):
    """An organized collection of metadata.

    A metadata report is iterable and it is also possible to directly
    retrieve an attribute using its ID.

    Attributes:
        metadataflow: The URN of the dataflow for which the report
            belongs.
        targets: The URN(s) of SDMX artefact(s) to which the report relates.
        attributes: The list of metadata attributes included in the report.
            Attributes may contain other attributes.
        metadataProvisionAgreement: reference to a metadata provision
            agreement
        publicationPeriod: The reporting period to which the metadata report
            relates
        publicationYear: The year when the report was published
        reportingBegin: The oldest period to which the report relates.
        reportingEnd: The most recent period to which the report relates.
        action: The action to be performed by the receiver.
    """

    metadataflow: str = ""
    targets: Sequence[str] = ()
    attributes: Sequence[MetadataAttribute] = ()
    metadataProvisionAgreement: Optional[str] = None
    publicationPeriod: Optional[str] = None
    publicationYear: Optional[str] = None
    reportingBegin: Optional[str] = None
    reportingEnd: Optional[str] = None
    action: Optional[ActionType] = None

    def __iter__(self) -> Iterator[MetadataAttribute]:
        """Return an iterator over the list of report attributes."""
        yield from self.attributes

    def __len__(self) -> int:
        """Return the number of attributes in the report."""
        return self.__get_count(self.attributes)

    def __getitem__(self, id_: str) -> Optional[MetadataAttribute]:
        """Return the attribute identified by the given ID."""
        return self.__extract_attr(self.attributes, id_)

    def __get_count(self, attributes: Sequence[MetadataAttribute]) -> int:
        """Return the number of attributes at all levels."""
        count = len(attributes)
        for attr in attributes:
            if attr.attributes:
                count += self.__get_count(attr.attributes)
        return count

    def __extract_attr(
        self, attributes: Sequence[MetadataAttribute], id_: str
    ) -> Optional[MetadataAttribute]:
        if "." in id_:
            ids = id_.split(".")
            out = list(filter(lambda attr: attr.id == ids[0], attributes))
            if out:
                pkey = ".".join(ids[1:])
                return self.__extract_attr(out[0].attributes, pkey)
        else:
            out = list(filter(lambda attr: attr.id == id_, attributes))
            if out:
                return out[0]
        return None

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        processed_output = []
        for attr, value, *_ in self.__rich_repr__():  # type: ignore[misc]
            # str is taken as a Sequence, so we need to check it's not a str
            if isinstance(value, Sequence) and not isinstance(value, str):
                # Handle non-empty lists
                if not value:
                    continue
                class_name = value[0].__class__.__name__
                if class_name == "MetadataAttribute":
                    class_name = "Metadata Attribute"
                value = f"{len(value)} {class_name.lower()}s"

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


def merge_attributes(
    attrs: Sequence[MetadataAttribute],
) -> Sequence[MetadataAttribute]:
    """Groups together the values of attributes with the same ID.

    The function assumes that an attribute will either have a
    value or will act as a container for other attributes. In
    case the attribute contains other attributes AND has a value,
    this function will NOT work as expected.

    Args:
        attrs: The list of attributes to be merged

    Returns:
        The list of (possibly merged) attributes
    """
    by_id: Dict[str, List[Any]] = defaultdict(list)
    sub_id = []

    for attr in attrs:
        if attr.attributes:
            sub_id.append(
                MetadataAttribute(
                    attr.id,
                    attr.value,
                    merge_attributes(attr.attributes),
                )
            )
        else:
            by_id[attr.id].append(attr.value)

    out = []
    out.extend(sub_id)
    for k, v in by_id.items():
        val = v if len(v) > 1 else v[0]
        out.append(MetadataAttribute(k, val))
    return out
