"""SDMX 1.0 CSV writer module."""

from copy import copy
from typing import Optional, Sequence

import pandas as pd

from pysdmx.io.pd import PandasDataset


def write(
    datasets: Sequence[PandasDataset], output_path: Optional[str] = None
) -> Optional[str]:
    """Write data to SDMX-CSV 1.0 format.

    Args:
        datasets: List of datasets to write.
          Must have the same components.
        output_path: Path to write the data to.
          If None, the data is returned as a string.

    Returns:
        SDMX CSV data as a string, if output_path is None.
    """
    # Link to pandas.to_csv documentation on sphinx:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html

    # Create a copy of the dataset
    dataframes = []
    for dataset in datasets:
        df: pd.DataFrame = copy(dataset.data)
        df.insert(0, "DATAFLOW", dataset.short_urn.split("=")[1])

        # Add additional attributes to the dataset
        for k, v in dataset.attributes.items():
            df[k] = v
        dataframes.append(df)

    # Concatenate the dataframes
    all_data = pd.concat(dataframes, ignore_index=True, axis=0)
    # Return the SDMX CSV data as a string
    return all_data.to_csv(output_path, index=False, header=True)
