"""Model for data-related artefacts."""

from datetime import datetime
from typing import Optional

from msgspec import Struct


class SeriesInfo(Struct, frozen=True):
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
        """Returns a human-friendly description."""
        out = []
        for k in self.__annotations__.keys():
            v = self.__getattribute__(k)
            if v:
                out.append(f"{k}={v}")
        return ", ".join(out)
