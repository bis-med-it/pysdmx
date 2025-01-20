"""Pandas SDMX Dataset."""

from pysdmx.__extras_check import __check_data_extra
from pysdmx.model.dataset import Dataset

__check_data_extra()

# E402 is needed here to ensure a clear message is used on missing import
import pandas as pd  # noqa: E402


class PandasDataset(Dataset, frozen=False, kw_only=True):
    """Class related to Dataset, using Pandas Dataframe.

    It is based on SDMX Dataset and has Pandas Dataframe compatibility to
    withhold data.

    Args:
        attributes: Attributes at dataset level.
        data: Pandas Dataframe.
        structure:
          URN or Schema related to this Dataset
          (DSD, Dataflow, ProvisionAgreement)
    """

    data: pd.DataFrame
