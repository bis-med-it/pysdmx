from typing import Any, Dict

import pandas as pd
from msgspec._core import Struct


class Dataset(Struct, frozen=False, kw_only=True):
    """Class containing the necessary attributes to create the Dataset.

    Args:
            attached_attributes: Attached attributes from the sdmx file.
            data: Dataframe.
            structure_type: Dataflow or DataStructure.
            unique_id: Combination of Agency_id, Id and Version.
    """

    attached_attributes: Dict[str, Any]
    data: pd.DataFrame
    unique_id: str
    structure_type: str
