"""SDMX 2.0 CSV writer module."""

from copy import copy

import pandas as pd

from pysdmx.model.dataset import Dataset


def writer(dataset: Dataset, output_path: str = None) -> str:
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
    for k, v in dataset.attached_attributes.items():
        df[k] = v

    # Insert two columns at the beginning of the data set
    df.insert(0, "STRUCTURE", dataset.structure_type)
    df.insert(1, "STRUCTURE_ID", dataset.unique_id)
    if "action" in dataset.attached_attributes:
        da_action = dataset.attached_attributes["action"]
        df.insert(2, "ACTION", da_action)

    # Convert the dataset into a csv file
    if output_path is not None:
        # Save the CSV file to the specified output path
        df.to_csv(output_path, index=False, header=True)

    # Return the SDMX CSV data as a string
    return df.to_csv(index=False, header=True)
