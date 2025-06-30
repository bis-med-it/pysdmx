"""Dataset module."""

from datetime import date, datetime
from enum import Enum
from typing import Any, Dict, Optional, Union

from msgspec import Struct

from pysdmx.model import Schema


class ActionType(Enum):
    """ActionType enumeration.

    Enumeration that withholds the Action type for writing purposes.
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
    """Core Dataset class."""

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
