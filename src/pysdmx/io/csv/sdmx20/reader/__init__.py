"""SDMX 2.0 CSV reader module."""

from io import StringIO
from typing import Dict

import pandas as pd

from pysdmx.errors import ClientError
from pysdmx.model.dataset import PandasDataset


def __generate_dataset_from_sdmx_csv(data: pd.DataFrame) -> PandasDataset:
    # Extract Structure type and structure id
    attached_attributes = {}

    if "ACTION" in data.columns:
        # Drop 'ACTION' column from DataFrame
        attached_attributes["action"] = data["ACTION"].iloc[0]
        data = data.drop(["ACTION"], axis=1)
    # For SDMX-CSV version 2, use 'STRUCTURE_ID'
    # column as the structure id and 'STRUCTURE' as the structure type
    structure_id = data["STRUCTURE_ID"].iloc[0]
    structure_type = data["STRUCTURE"].iloc[0]
    # Drop 'STRUCTURE' and 'STRUCTURE_ID' columns from DataFrame
    df_csv = data.drop(["STRUCTURE", "STRUCTURE_ID"], axis=1)

    urn = f"{structure_type}={structure_id}"
    # Extract dataset attributes from sdmx-csv (all values are the same)
    attributes = {
        col: df_csv[col].iloc[0]
        for col in df_csv.columns
        if df_csv[col].nunique() == 1
    }
    for col in attributes:
        df_csv = df_csv.drop(col, axis=1)

    # Return a Dataset object with the extracted information
    return PandasDataset(
        structure=urn,
        data=df_csv,
        attributes=attributes,
    )


def read(infile: str) -> Dict[str, PandasDataset]:
    """Reads csv file and returns a payload dictionary.

    Args:
        infile: Path to file, str.

    Returns:
        payload: dict.

    Raises:
        ClientError: If it is an invalid CSV file.
    """
    # Get Dataframe from CSV file
    df_csv = pd.read_csv(StringIO(infile))
    # Drop empty columns
    df_csv = df_csv.dropna(axis=1, how="all")

    # Determine SDMX-CSV version based on column names
    if (
        "STRUCTURE" not in df_csv.columns
        or "STRUCTURE_ID" not in df_csv.columns
    ):
        # Raise an exception if the CSV file is not in SDMX-CSV format
        raise ClientError(
            400,
            "Only SDMX-CSV 2.0 is allowed",
            "Invalid SDMX-CSV 2.0 file. "
            "Check the docs for the proper structure on content.",
        )

    # Convert all columns to strings
    df_csv = df_csv.astype("str")
    # Check if any column headers contain ':', indicating mode, label or text
    mode_label_text = any(":" in x for x in df_csv.columns)

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

    # Separate SDMX-CSV in different datasets per Structure ID
    list_df = [data for _, data in df_csv.groupby(id_column)]

    # Create a payload dictionary to store datasets with the
    # different unique_ids as keys
    payload = {}
    for df in list_df:
        # Generate a dataset from each subset of the DataFrame
        dataset = __generate_dataset_from_sdmx_csv(data=df)

        # Add the dataset to the payload dictionary
        payload[dataset.short_urn] = dataset

    # Return the payload generated
    return payload
