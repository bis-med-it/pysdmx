"""Pandas SDMX Dataset."""

import pandas as pd

from pysdmx.model.dataset import Dataset


class PandasDataset(Dataset, frozen=False, kw_only=True):
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
