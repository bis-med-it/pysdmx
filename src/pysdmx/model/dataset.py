"""Dataset module."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from msgspec import Struct

from pysdmx.model import Schema


class ActionType(Enum):
    """Enumeration that defines the Dataset Action.

    Arguments:
        Append: Append data to an existing dataset.
        Replace: Replace the existing dataset with new data.
        Delete: Delete the data provided from the data source.
        Information: Provide information about the dataset
          without modifying it.

    """

    Append = "Append"
    Replace = "Replace"
    Delete = "Delete"
    Information = "Information"

    def __str__(self) -> str:
        """Return the action as a string."""
        return self.name.capitalize()

    def __repr__(self) -> str:
        """Action String representation."""
        return f"{self.__class__.__name__}.{self._name_}"


class SeriesInfo(Struct, frozen=True, repr_omit_defaults=True):
    """A group of related data, such as a time series, or a case series.

    Attributes:
        id: The unique ID for the series, such as a series key.
        name: The series's name (aka title), if any.
        obs_count: The number of observations available in the series.
        start_period: The oldest period for which data are available.
        end_period: The oldest period for which data are available.
        last_updated: When the series was last updated.
        is_active: Whether the series is still relevant or has been
            discontinued.
    """

    id: str
    name: Optional[str] = None
    obs_count: Optional[int] = None
    start_period: Optional[str] = None
    end_period: Optional[str] = None
    last_updated: Optional[datetime] = None
    is_active: bool = True

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


class Dataset(Struct, frozen=False, repr_omit_defaults=True, kw_only=True):
    """An organised collection of data.

    It includes metadata such as the structure of the dataset, attributes,
    action type, reporting periods and publication details.

    Args:
        structure: The structure referenced from a dataset,
          which can be a string (short_urn) or a Schema object.
        attributes: dictionary of attributes at dataset level, with its values.
        action: Defines the :class:`Action <pysdmx.model.dataset.ActionType>`
          of the dataset, default is ActionType.Information.
        reporting_begin: The start date for reporting, if applicable.
        reporting_end: The end date for reporting, if applicable.
        data_extraction_date: The date when the data was extracted.
        valid_from: The start date for the validity of the dataset.
        valid_to: The end date for the validity of the dataset.
        publication_year: The year of publication of the dataset.
        publication_period: The period of publication of the dataset.
        set_id: An optional identifier for the dataset.
    """

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
            return self.structure
        else:
            return self.structure.short_urn

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
