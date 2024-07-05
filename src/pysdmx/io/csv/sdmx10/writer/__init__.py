"""SDMX 1.0 CSV writer module."""
from copy import copy
from typing import Any

import pandas as pd


class Dataset:
    """Class containing the necessary attributes to create the Dataset.

    Args:
            attached_attributes: Attached attributes from the xml file.
            data: Dataframe.
            structure_type: Generic or Specific.
            unique_id: DimensionAtObservation.
    """

    __slots__ = ("attached_attributes", "data", "unique_id", "structure_type")

    def __init__(
            self,
            attached_attributes: Any,
            data: Any,
            unique_id: Any,
            structure_type: Any,
    ):
        """Attributes."""
        self.attached_attributes = attached_attributes
        self.data = data
        self.unique_id = unique_id
        self.structure_type = structure_type


def to_sdmx_csv(dataset: Dataset, version: int, output_path: str = None):
    """
    Converts a dataset to an SDMX CSV format

    :param version: The SDMX-CSV version (1.2)
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

    # Add additional attributes to the dataset
    for k, v in dataset.attached_attributes.items():
        df[k] = v

    if version == 1:
        df.insert(0, 'DATAFLOW', dataset.unique_id)

    else:
        raise Exception('Invalid SDMX-CSV version.')

    # Convert the dataset into a csv file
    if output_path is not None:
        # Save the CSV file to the specified output path
        df.to_csv(output_path, index=False, header=True)

    # Return the SDMX CSV data as a string
    return df.to_csv(index=False, header=True)
