"""Dataset module."""

from datetime import date, datetime
from typing import Any, Dict, Optional, Union

from msgspec import Struct

from pysdmx.model import Schema
from pysdmx.model.message import ActionType


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


class Dataset(Struct, frozen=False, kw_only=True):
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
            structure_type, unique_id = self.structure.split("=", maxsplit=1)
            structure = structure_type.rsplit(".", maxsplit=1)[1]
            return f"{structure}={unique_id}"
        else:
            s = self.structure
            return f"{s.context}={s.agency}:{s.id}({s.version})"
