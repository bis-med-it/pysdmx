"""Pandas SDMX Dataset."""

from pysdmx.__extras_check import __check_data_extra
from pysdmx.model.dataset import Dataset

__check_data_extra()

# E402 is needed here to ensure a clear message is used on missing import
import pandas as pd  # noqa: E402


class PandasDataset(Dataset, frozen=False, kw_only=True):
    """A Dataset that is backed by a Pandas DataFrame.

    Args:
        data: Pandas Dataframe to contain SDMX data.
    """

    data: pd.DataFrame
