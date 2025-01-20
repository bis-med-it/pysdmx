"""SDMX 2.0 CSV writer module."""

from copy import copy
from typing import Optional, Sequence

import pandas as pd

from pysdmx.io.csv.sdmx20 import SDMX_CSV_ACTION_MAPPER
from pysdmx.io.pd import PandasDataset


def write(
    datasets: Sequence[PandasDataset], output_path: Optional[str] = None
) -> Optional[str]:
    """Write data to SDMX-CSV 2.0 format.

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

    dataframes = []
    for dataset in datasets:
        # Create a copy of the dataset
        df: pd.DataFrame = copy(dataset.data)

        # Add additional attributes to the dataset
        for k, v in dataset.attributes.items():
            df[k] = v

        structure_ref, unique_id = dataset.short_urn.split("=", maxsplit=1)
        if structure_ref in ["DataStructure", "Dataflow"]:
            structure_ref = structure_ref.lower()
        else:
            structure_ref = "dataprovision"

        # Insert two columns at the beginning of the data set
        df.insert(0, "STRUCTURE", structure_ref)
        df.insert(1, "STRUCTURE_ID", unique_id)
        action_value = SDMX_CSV_ACTION_MAPPER[dataset.action]
        df.insert(2, "ACTION", action_value)

        dataframes.append(df)

    all_data = pd.concat(dataframes, ignore_index=True, axis=0)

    # Convert the dataset into a csv file
    return all_data.to_csv(output_path, index=False, header=True)
