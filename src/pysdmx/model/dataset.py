"""Dataset module."""

from datetime import date
from typing import Any, Dict, Optional, Union

from msgspec import Struct
import pandas as pd

from pysdmx.model import Schema
from pysdmx.model.message import ActionType


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
