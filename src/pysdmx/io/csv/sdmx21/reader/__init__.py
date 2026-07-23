"""SDMX 2.1 CSV reader module."""

from io import StringIO
from typing import Sequence

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.csv.__csv_aux_reader import __generate_dataset_from_sdmx_csv
from pysdmx.io.pd import PandasDataset
from pysdmx.toolkit.pd._data_utils import drop_labels


def read(input_str: str) -> Sequence[PandasDataset]:
    """Reads csv data and returns a sequence of Datasets.

    Args:
        input_str: str.

    Returns:
        A Sequence of Pandas Datasets.

    Raises:
        Invalid: If it is an invalid CSV file.
    """
    # Get Dataframe from CSV file
    df_csv = pd.read_csv(
        StringIO(input_str), keep_default_na=False, na_values=[]
    )
    # Drop empty columns
    df_csv = df_csv.dropna(axis=1, how="all")

    # Determine SDMX-CSV version based on column names
    if (
        "STRUCTURE" not in df_csv.columns
        or "STRUCTURE_ID" not in df_csv.columns
    ):
        # Raise an exception if the CSV file is not in SDMX-CSV format
        raise Invalid(
            "Only SDMX-CSV 2.1 is allowed",
            "Invalid SDMX-CSV 2.1 file. "
            "Check the docs for the proper structure on content.",
        )

    # Convert all columns to strings
    df_csv = df_csv.astype(str).replace({"nan": "NaN", "<NA>": "NaN"})
    # Strip the labels, if any, keeping only the ids. The structure id
    # label is stripped later, in __generate_dataset_from_sdmx_csv.
    df_csv = drop_labels(df_csv)

    # Grouping columns to separate datasets
    grouping_columns = ["STRUCTURE", "STRUCTURE_ID"]
    # Separate SDMX-CSV in different datasets per Structure ID
    list_df = [data for _, data in df_csv.groupby(grouping_columns)]

    # Create a payload dictionary to store datasets with the
    # different unique_ids as keys
    payload = []
    for df in list_df:
        # Generate a dataset from each subset of the DataFrame
        dataset = __generate_dataset_from_sdmx_csv(data=df, references_21=True)

        # Add the dataset to the payload dictionary
        payload.append(dataset)

    # Return the payload generated
    return payload
