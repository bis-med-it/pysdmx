"""Model for SDMX dataflows and related structures (like schemas).

``pysdmx`` is dataflow-centric, another area where ``pysdmx`` is
opinionated. As such, when retrieving information about a dataflow,
information typically provided via the data structure (and related
structures like concept schemes and codelists) is already provided
as part of the response.
"""

from collections import Counter, UserList
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Iterable, Literal, Optional, Sequence, Union

from msgspec import Struct

from pysdmx.errors import Invalid
from pysdmx.model.__base import (
    Agency,
    DataProvider,
    ItemReference,
    MaintainableArtefact,
)
from pysdmx.model.code import Codelist, Hierarchy
from pysdmx.model.concept import Concept, DataType, Facets


class Role(str, Enum):
    """The various roles a component can play."""

    DIMENSION = "D"
    """The component helps identifying data (e.g. primary key)."""
    MEASURE = "M"
    """The component holds a value we measure or collect."""
    ATTRIBUTE = "A"
    """The component provides descriptive information about the data."""

    def __str__(self) -> str:
        """Return the role as a string."""
        return self.name.capitalize()

    def __repr__(self) -> str:
        """Role String representation."""
        return f"{self.__class__.__name__}.{self._name_}"


class ArrayBoundaries(Struct, frozen=True, repr_omit_defaults=True):
    """The minimum and maximum number of items in the SDMX array."""

    min_size: int = 0
    max_size: Optional[int] = None

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


class Component(
    Struct, frozen=True, omit_defaults=True, repr_omit_defaults=True
):
    """A component of a dataset (aka **variable**), such the frequency.

    Concepts are used to **describe the relevant characteristics** of a
    statistical domain. For example, exchanges rates might be described with
    components such as the numerator currency, the denominator currency,
    the type of exchange rates, etc.

    Some of these components are expected to be useful **across statistical
    domains**. Examples of such components include the frequency, the
    observation status, the confidentiality, etc.

    When using components to describe the expected structure of a statistical
    domain, data stewards distinguish between the components that represent
    what is being captured (i.e. the **measures**), the components that help
    uniquely **identifying** the measures (i.e. the dimensions) and the
    components that provide additional **descriptive information** about the
    measures (i.e. the attributes). This is the **component role**. The role
    can be *D* (for Dimension), *A* (for Attribute) or *M* (for Measure).

    While dimensions and measures are typically mandatory, attributes may be
    either **mandatory or optional**. This is captured in the *required*
    property using a boolean value (*true* for mandatory components, *false*
    otherwise). This may vary with the statistical domain, i.e. a mandatory
    component within a particular domain may be optional in another.

    While the value of some attributes is expected to potentially vary with
    each *measurement* (aka observation or data point), some others must be
    unique across all observations sharing the same (sub)set of dimension
    values. This is captured in the *attachment_level* property, which can be
    one of: *D* (for Dataset), *O* (for Observation), any string identifying a
    component ID (FREQ) or comma-separated list of component IDs
    (FREQ,REF_AREA). The latter can be used to identify the dimension, group
    or series to which the attribute is attached. The attachment level of a
    component may vary with the statistical domain, i.e. a component attached
    to a series in a particular domain may be attached to, say, the dataset in
    another domain.

    The *codes* field indicates the expected (i.e. allowed) set of values a
    component can take within a particular domain. In addition to
    (or instead of) a set of codes, additional details about the expected
    format may be found in the *facets* and *dtype* fields.


    Attributes:
        id: A unique identifier for the component (e.g. FREQ).
        required: Whether the component must have a value.
        role: The role played by the component.
        local_dtype: The component's local data type (string, number, etc.).
        local_facets: Additional local details such as the component's minimum
            length.
        name: The component's name.
        description: Additional descriptive information about the component.
        local_codes: The expected local values for the component (e.g. currency
            codes).
        attachment_level: The attachment level (if role = A only).
            Attributes can be attached at different levels such as
            D (for dataset-level attributes), O (for observation-level
            attributes) or a combination of dimension IDs, separated by
            commas, for series- and group-level attributes).
            A post_init check makes this attribute mandatory for attributes.
        array_def: Any additional constraints for array types.
    """

    id: str
    required: bool
    role: Role
    concept: Union[Concept, ItemReference]
    local_dtype: Optional[DataType] = None
    local_facets: Optional[Facets] = None
    name: Optional[str] = None
    description: Optional[str] = None
    local_codes: Union[Codelist, Hierarchy, None] = None
    attachment_level: Optional[str] = None
    array_def: Optional[ArrayBoundaries] = None
    urn: Optional[str] = None

    def __post_init__(self) -> None:
        """Validate the component."""
        if self.role != Role.ATTRIBUTE and self.attachment_level is not None:
            raise Invalid(
                "Validation Error",
                (
                    "The attachment_level field is "
                    "only allowed for attribute components"
                ),
            )
        if self.role == Role.ATTRIBUTE and self.attachment_level is None:
            raise Invalid(
                "Validation Error",
                "The attachment_level field is mandatory "
                "for attribute components",
            )

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


class Components(UserList[Component]):
    """A collection of components describing the data."""

    def __init__(self, iterable: Iterable[Component]) -> None:
        """Create a new schema with the supplied components."""
        self.__validate_iterable(iterable, True)
        super().__init__(iterable)

    def __setitem__(self, index: Any, item: Any) -> None:
        """Add a component at the requested index."""
        self.__validate_comp(item)
        super().__setitem__(index, item)

    def __getitem__(self, i: Any) -> Any:
        """Return the component matching the supplied id or position.

        Args:
            i: The id of the component to be returned, or
                its position in the collection, or a slice.

        Returns:
            The component matching the supplied id or position, or
            multiple components in case slice is used.
        """
        if isinstance(i, (int, slice)):
            return super().__getitem__(i)
        else:
            out = list(filter(lambda item: item.id == i, self.data))
            if len(out) == 0:
                return None
            else:
                return out[0]

    def insert(self, i: int, item: Component) -> None:
        """Add a component at the requested index."""
        self.__validate_comp(item)
        super().insert(i, item)

    def append(self, item: Component) -> None:
        """Add a component to the existing list of components."""
        self.__validate_comp(item)
        super().append(item)

    def extend(self, other: Iterable[Component]) -> None:
        """Add the components to the existing list of components."""
        self.__validate_iterable(other, False)
        super().extend(other)

    @property
    def dimensions(self) -> Sequence[Component]:
        """Return the list of dimensions.

        Dimensions are components that contribute to the unique identification
        of a piece of data (aka an observation or data point). The
        combination of the values for all dimensions of an observation can
        therefore be seen as the observation's *primary key*.

        Returns:
            The list of dimensions
        """
        return [c for c in self.data if c.role == "D"]

    @property
    def attributes(self) -> Sequence[Component]:
        """Return the list of attributes.

        Attributes are components that provide descriptive information about
        some piece of data (aka an observation or data point).

        Returns:
            The list of attributes
        """
        return [c for c in self.data if c.role == "A"]

    @property
    def measures(self) -> Sequence[Component]:
        """Return the list of measures.

        Measures are components that hold the measured values.

        Returns:
            The list of measures
        """
        return [c for c in self.data if c.role == "M"]

    def __validate_iterable(
        self,
        coll: Iterable[Component],
        is_init: bool,
    ) -> None:
        if len(list(coll)) > 0:
            for fld in coll:
                self.__validate_comp(fld, is_init)
            counter = Counter([f.id for f in coll])
            dup = [i[0] for i in counter.items() if i[1] > 1]
            if len(dup) > 0:
                raise Invalid(
                    "Validation Error",
                    f"There are duplicates in the collection: {dup}",
                )

    def __validate_comp(self, fld: Component, is_init: bool = False) -> None:
        if not isinstance(fld, Component):
            raise Invalid(
                "Validation Error",
                f"Unexpected type. Expected Component but got: {type(fld)}",
            )
        if not is_init:
            ids = [f.id for f in self.data]
            if fld.id in ids:
                raise Invalid(
                    "Validation Error",
                    f"There is already a component with ID: {fld.id}",
                )

    def __str__(self) -> str:
        """Custom string representation without the class name."""
        return f"data: {len(self)} components"

    def __repr__(self) -> str:
        """Custom __repr__ that omits empty sequences."""
        attrs = []
        for attr, value in self.__dict__.items():
            attrs.append(f"{attr}={repr(value)}")
        return f"{self.__class__.__name__}({', '.join(attrs)})"


class DataflowInfo(
    Struct, frozen=True, omit_defaults=True, repr_omit_defaults=True
):
    """Extended information about a dataflow.

    The information includes:

    - Some basic metadata about the dataflow (such as its ID and name).
    - Some useful metrics such as the number of observations.
    - The expected structure of data (i.e. the data schema), including
      the expected components, their types, etc.

    Attributes:
        id: The identifier of the dataflow (e.g. CBS).
        components: The data structure, i.e. the components, their types, etc.
        agency: The organization responsible for the data (e.g. BIS).
        name: The dataflow's name (e.g. Consolidated Banking Statistics).
        description: Additional descriptive information about the dataflow.
        version: The dataflow version.
        providers: The organizations providing the data.
        series_count: The number of series available in the dataflow.
        obs_count: The number of observations available in the dataflow.
        start_period: The oldest period for which data are available.
        end_period: The oldest period for which data are available.
        last_updated: When the dataflow was last updated.
        dsd_ref: The URN of the data structure used by the dataflow.
    """

    id: str
    components: Components
    agency: Agency
    name: Optional[str] = None
    description: Optional[str] = None
    version: str = "1.0"
    providers: Sequence[DataProvider] = ()
    series_count: Optional[int] = None
    obs_count: Optional[int] = None
    start_period: Optional[str] = None
    end_period: Optional[str] = None
    last_updated: Optional[datetime] = None
    dsd_ref: Optional[str] = None

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


class Schema(Struct, frozen=True, omit_defaults=True, repr_omit_defaults=True):
    """The allowed content within a certain context.

    This is the equivalent to the result of a schema query in the
    SDMX-REST API.

    The response contains the list of allowed values for the
    selected context (one of datastructure, dataflow or
    provisionagreement), and is typically used for validation
    purposes.

    Attributes:
        context: The context for which the schema is provided.
            One of datastructure, dataflow or provisionagreement.
        agency: The agency maintaining the context (e.g. BIS).
        id: The ID of the context (e.g. BIS_MACRO).
        components: The list of components along with their
            allowed values, types, etc.
        version: The context version (e.g. 1.0)
        artefacts: The URNs of the artefacts used to generate the
            schema. This will typically include the URNs of data
            structures, codelists, concept schemes, content
            constraints, etc.
        generated: When the schema was generated. This is useful
            for metadata synchronization purposes. For example,
            if any of the artefacts listed under the artefacts
            property has been updated after the schema was
            generated, you might want to regenerate the schema.
    """

    context: Literal["datastructure", "dataflow", "provisionagreement"]
    agency: str
    id: str
    components: Components
    version: str = "1.0"
    artefacts: Sequence[str] = ()
    generated: datetime = datetime.now(timezone.utc)

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
                # If the value is a list of artefacts, we can summarize it
                if attr == "artefacts":
                    class_name = "Artefact"
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

    @property
    def short_urn(self) -> str:
        """Returns a short URN for the schema."""
        SHORT_URN_MAPPING = {
            "datastructure": "DataStructure",
            "dataflow": "Dataflow",
            "provisionagreement": "ProvisionAgreement",
        }
        sdmx_type = SHORT_URN_MAPPING[self.context]
        return f"{sdmx_type}={self.agency}:{self.id}({self.version})"


class DataStructureDefinition(MaintainableArtefact, frozen=True, kw_only=True):
    """A collection of metadata concepts.

    Attributes:
        agency: The organization responsible for the data structure.
        annotations: The list of annotations attached to the data structure.
        id: The identifier of the data structure.
        description: descriptive information about the data structure.
        is_external_reference: Whether the data structure is an external
            reference.
        is_final: Whether the data structure is final.
        name: The data structure's name.
        service_url: The URL of the service providing the data structure.
        structure_url: The URL of the structure.
        uri: The URI of the data structure.
        urn: The URN of the data structure.
        valid_from: The date from which the data structure is valid.
        valid_to: The date until which the data structure is valid.
        version: The version of the data structure.
        evolving_structure: Whether new dimensions may be added under a
            minor version update.
    """

    components: Components
    evolving_structure: bool = False

    def __extract_artefacts(self) -> Sequence[str]:
        """Extract the artefacts used to generate the schema."""
        out = []
        for c in self.components:
            if c.local_codes:
                out.append(c.local_codes.urn)
            # Concept URNs
            if isinstance(c.concept, Concept):
                out.append(c.concept.urn)
                if c.concept.codes:
                    out.append(c.concept.codes.urn)
            else:
                urn_header = "urn:sdmx:org.sdmx.infomodel.conceptscheme."
                out.append(urn_header + str(c.concept))
        result = list({a for a in out if a})
        return result

    def to_schema(self) -> Schema:
        """Generates a Schema class from the DataStructureDefinition."""
        return Schema(
            context="datastructure",
            agency=(
                self.agency.id
                if isinstance(self.agency, Agency)
                else self.agency
            ),
            id=self.id,
            components=self.components,
            version=self.version,
            artefacts=self.__extract_artefacts(),
        )

    @property
    def short_urn(self) -> str:
        """Returns a short URN for the data structure."""
        return f"DataStructure={self.agency}:{self.id}({self.version})"


class Dataflow(
    MaintainableArtefact,
    frozen=True,
    omit_defaults=True,
    tag=True,
):
    """A flow of data that providers will provide."""

    structure: Optional[Union[DataStructureDefinition, str]] = None


class ProvisionAgreement(
    MaintainableArtefact, frozen=True, omit_defaults=True, kw_only=True
):
    """Link between a data provider and dataflow."""

    dataflow: str
    provider: str
