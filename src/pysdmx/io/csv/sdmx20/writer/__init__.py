"""SDMX 2.0 CSV writer module."""

from copy import copy
from typing import Optional

import pandas as pd

from pysdmx.io.csv.sdmx20 import SDMX_CSV_ACTION_MAPPER
from pysdmx.io.pd import PandasDataset


def writer(
    dataset: PandasDataset, output_path: Optional[str] = None
) -> Optional[str]:
    """Converts a dataset to an SDMX CSV format.

    Args:
        dataset: dataset
        output_path: output_path

    Returns:
        SDMX CSV data as a string
    """
    # Link to pandas.to_csv documentation on sphinx:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html

    # Create a copy of the dataset
    df: pd.DataFrame = copy(dataset.data)

    # Add additional attributes to the dataset
    for k, v in dataset.attributes.items():
        df[k] = v

    structure_ref, unique_id = dataset.short_urn.split("=", maxsplit=1)
    if structure_ref in ["DataStructure", "DataFlow"]:
        structure_ref = structure_ref.lower()
    else:
        structure_ref = "dataprovision"

    # Insert two columns at the beginning of the data set
    df.insert(0, "STRUCTURE", structure_ref)
    df.insert(1, "STRUCTURE_ID", unique_id)
    action_value = SDMX_CSV_ACTION_MAPPER[dataset.action]
    df.insert(2, "ACTION", action_value)

    # Convert the dataset into a csv file
    return df.to_csv(output_path, index=False, header=True)
