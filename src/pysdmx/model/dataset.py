"""Dataset module."""

from datetime import date, datetime
from typing import Any, Dict, Iterator, Optional, Sequence, Union

from msgspec import Struct
import pandas as pd

from pysdmx.model.__base import DataProvider
from pysdmx.model.dataflow import Schema
from pysdmx.model.message import ActionType
from pysdmx.model.metadata import MetadataReport


class _ComponentValue(Struct, frozen=True):
    """An abstract class representing an instance of a component.

    This class is not meant to be used directly. Instead, it is meant
    to be inherited by the Dimension, DataAttribute and Measure classes.

    Attributes:
        id: The component ID (e.g. FREQ)
        value: The component value (e.g. M)
    """

    id: str
    value: Any


class DimensionValue(_ComponentValue, Struct, frozen=True):
    """The value of the instance a Dimension.

    For example, `FREQ=M`, where `FREQ` is the ID of the dimension
    and `M` is its value.
    """


class DataAttributeValue(_ComponentValue, Struct, frozen=True):
    """The value of the instance a Data Attribute.

    For example, `CONF_STATUS=F`, where `CONF_STATUS` is the ID of the
    data attribute and `F` is its value.
    """


class MeasureValue(_ComponentValue, Struct, frozen=True):
    """The value of the instance a Measure.

    For example, `OBS_VALUE=42`, where `OBS_VALUE` is the ID of the
    measure and `42` is its value.
    """


class _Package(Struct, frozen=True):
    """An abstract class representing a "package" with data and/or attributes.

    A package is identified by a key and may have data attributes and/or
    reference metadata attached to it.

    This class is not meant to be used directly. Instead, it is meant
    to be inherited by concrete packages, such as Observation, Series, Group
    and Dataset.

    Attributes:
        key: A string acting as unique identified for the package. This
            corresponds to the list of dimension values, in the order of
            their definition in the Data Structure Definition, separated
            by a dot. In case the dimension value contains a dot, it will
            be escaped by a backslash. In case the dimension value contains
            a backslash, that backslash will be escaped by another backslash.
            In case the value for a dimension is missing (e.g. the package
            represents a dataset, a group or a series), this will be
            represented with a * in the key.
        dimensions: The list of dimension values.
        attributes: The list of data attribute values attached to the
            package.
        ref_meta: The list of metadata reports attached to the package.
    """

    key: str
    dimensions: Sequence[DimensionValue]
    attributes: Optional[Sequence[DataAttributeValue]] = None
    metadata: Optional[Sequence[MetadataReport]] = None


class Observation(_Package, Struct, frozen=True, kw_only=True):
    """An observation is a type of package that contains measure values.

    It inherits all the properties from Package (key, dimensions, attributes
    and ref_meta), to which it adds a measures property.
    """

    measures: Sequence[MeasureValue]


class _ObsPackage(_Package, Struct, frozen=True, kw_only=True):
    """An abstract class representing a package containing observations.

    This class is not meant to be used directly. Instead, it is meant
    to be inherited by concrete packages that may contain observations,
    i.e. Series and Dataset.

    It inherits all the properties from Package (key, dimensions, attributes
    and ref_meta), to which it adds a measures property.

    Attributes:
        observations: An iterator of observations. An iterator is used
            to allow for scenarios where the entire set of observations
            does not fit into memory.
        obs_count: The number of observations contained in the package.
        start_period: The oldest period in the list of observations.
        end_period: The most recent period in the list of observations.
        last_updated: When the observations contained in the package were
            last updated.
    """

    observations: Iterator[Observation] = ().__iter__()
    obs_count: Optional[int] = None
    start_period: Optional[str] = None
    end_period: Optional[str] = None
    last_updated: Optional[datetime] = None


class Series(_ObsPackage, Struct, frozen=True, kw_only=True):
    """A package of related observations and additional metadata."""


class Group(_Package, Struct, frozen=True, kw_only=True):
    """A package whose sole purpose is to contain metadata."""


class Dataset(_ObsPackage, Struct, frozen=True, kw_only=True):
    """An organized collection of data.

    It inherits all the properties from the Observation Package and
    adds a few of its own.

    Attributes:
        packages: An iterator of packages. An iterator is used
            to allow for scenarios where the entire set of packages
            does not fit into memory.
        provider: The provider of the data contained in the dataset.
        structure: Either a schema describing the structure of the data
            contained in the dataset, or a string representing the SDMX URN
            of that structure.
    """

    packages: Iterator[Union[Group, Series, Observation]]
    provider: Optional[DataProvider] = None
    structure: Union[Schema, str]  # Schema or the SDMX URN of the structure

    @property
    def groups(self) -> Iterator[Group]:
        """Get the packages of type `Group`."""
        return (p for p in self.packages if isinstance(p, Group))

    @property
    def series(self) -> Iterator[Series]:
        """Get the packages of type `Series`."""
        return (p for p in self.packages if isinstance(p, Series))


class PandasDataset(Struct, frozen=False, kw_only=True):
    """Class related to Dataset, using Pandas Dataframe.

    It is based on SDMX Dataset and has Pandas Dataframe compatibility to
    withhold data.

    Args:
        attributes: Attributes at dataset level-
        data: Dataframe.
        structure:
        URN or Schema related to this Dataset
        (DSD, Dataflow, ProvisionAgreement)
        short_urn: Combination of Agency_id, Id and Version.
    """

    data: pd.DataFrame
    structure: Union[str, Schema]
    attributes: Dict[str, Any] = {}
    action: ActionType = ActionType.Information
    reporting_begin: Optional[date] = None
    reporting_end: Optional[date] = None
    data_extraction_date: Optional[date] = None
    valid_from: Optional[date] = None
    valid_to: Optional[date] = None
    publication_year: Optional[date] = None
    publication_period: Optional[date] = None
    set_id: Optional[str] = None

    @property
    def short_urn(self) -> str:
        """Meaningful part of the URN.

        Returns:
            URN formatted string
        """
        if isinstance(self.structure, str):
            structure_type, unique_id = self.structure.split("=", maxsplit=1)
            structure = structure_type.rsplit(".", maxsplit=1)[1]
            return f"{structure}={unique_id}"
        else:
            s = self.structure
            return f"{s.context}={s.agency}:{s.id}({s.version})"
