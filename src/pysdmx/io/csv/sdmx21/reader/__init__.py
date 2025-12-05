"""SDMX 2.1 CSV reader module."""

from io import StringIO
from typing import Sequence

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.csv.__csv_aux_reader import __generate_dataset_from_sdmx_csv
from pysdmx.io.pd import PandasDataset


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
    df_csv = df_csv.astype(str).replace({"nan": "", "<NA>": ""})
    # Check if any column headers contain ':', indicating mode, label or text
    mode_label_text = any(":" in x for x in df_csv.columns)
    # if values in the columns contain ':', split them
    for col in df_csv.columns[2:]:
        df_csv[col] = (
            df_csv[col]
            .astype(str)
            .apply(lambda x: x.split(":")[0] if ":" in x else x)
        )

    id_column = "STRUCTURE_ID"
    # If mode, label or text is present, modify the DataFrame
    if mode_label_text:
        # Split the ID column to remove mode, label or text
        df_csv[id_column] = df_csv[id_column].map(lambda x: x.split(": ")[0])
        # Split the other columns to remove mode, label, or text
        sequence = 3
        for x in df_csv.columns[sequence:]:
            df_csv[x.split(":")[0]] = df_csv[x].map(
                lambda x: x.split(": ", 2)[0], na_action="ignore"
            )
            # Delete the original columns
            del df_csv[x]

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
