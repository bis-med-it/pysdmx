"""SDMX 1.0 CSV writer module."""

from copy import copy
from pathlib import Path
from typing import Optional

import pandas as pd

from pysdmx.io.pd import PandasDataset


def writer(
    dataset: PandasDataset, output_path: Optional[Path] = None
) -> Optional[str]:
    """Converts a dataset to an SDMX CSV format.

    Args:
        dataset: dataset
        output_path: Path to file, if None, returns the
          SDMX CSV data as a string

    Returns:
        SDMX CSV data as a string
    """
    # Link to pandas.to_csv documentation on sphinx:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html

    # Create a copy of the dataset
    df: pd.DataFrame = copy(dataset.data)
    df.insert(0, "DATAFLOW", dataset.short_urn.split("=")[1])

    # Add additional attributes to the dataset
    for k, v in dataset.attributes.items():
        df[k] = v

    # Return the SDMX CSV data as a string
    return df.to_csv(output_path, index=False, header=True)
