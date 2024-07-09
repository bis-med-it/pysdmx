"""SDMX 1.0 CSV writer module."""
from copy import copy

import pandas as pd

from pysdmx.model.dataset import Dataset


def writer(dataset: Dataset, output_path: str = None):
    """
    Converts a dataset to an SDMX CSV format

    :param output_path: The path where the resulting
                        SDMX CSV file will be saved

    :return: The SDMX CSV data as a string if no output path is provided

    .. important::

        The SDMX CSV version must be 1 or 2. Please refer to this link
        for more info:
        https://wiki.sdmxcloud.org/SDMX-CSV

        Uses pandas.Dataframe.to_csv with specific parameters to ensure
        the file is compatible with the SDMX-CSV standard (e.g. no index,
        uses header, comma delimiter, custom column names
        for the first two columns)
    """

    # Link to pandas.to_csv documentation on sphinx:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html

    # Create a copy of the dataset
    df: pd.DataFrame = copy(dataset.data)
    df['DATAFLOW'] = dataset.unique_id
    # Add additional attributes to the dataset
    for k, v in dataset.attached_attributes.items():
        df[k] = v

    # Convert the dataset into a csv file
    if output_path is not None:
        # Save the CSV file to the specified output path
        df.to_csv(output_path, index=False, header=True)

    # Return the SDMX CSV data as a string
    return df.to_csv(index=False, header=True)


