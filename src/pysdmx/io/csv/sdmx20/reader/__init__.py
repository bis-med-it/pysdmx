"""SDMX 2.0 CSV reader module."""

from io import StringIO
from typing import Dict

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model.message import ActionType

ACTION_SDMX_CSV_MAPPER_READING = {
    "A": ActionType.Append,
    "D": ActionType.Delete,
    "R": ActionType.Replace,
    "I": ActionType.Information,
}


def __generate_dataset_from_sdmx_csv(data: pd.DataFrame) -> PandasDataset:
    # Extract Structure type and structure id
    action = ActionType.Information
    if "ACTION" in data.columns:
        unique_values = list(data["ACTION"].unique())
        if len(unique_values) > 1 and "D" in unique_values:
            unique_values.remove("D")
            data = data[data["ACTION"] != "D"]
        if len(unique_values) == 1:  # If there is only one value, use it
            action_value = unique_values[0]
            if action_value not in ACTION_SDMX_CSV_MAPPER_READING:
                raise Invalid(
                    "Invalid value on ACTION column",
                    "Invalid SDMX-CSV 2.0 file. "
                    "Check the docs for the proper values on ACTION column.",
                )
            action = ACTION_SDMX_CSV_MAPPER_READING[action_value]
        else:
            raise Invalid(
                "Invalid value on ACTION column",
                "Invalid SDMX-CSV 2.0 file. "
                "Cannot have more than one value on ACTION column, "
                "or 2 if D is present",
            )
    # For SDMX-CSV version 2, use 'STRUCTURE_ID'
    # column as the structure id and 'STRUCTURE' as the structure type
    structure_id = data["STRUCTURE_ID"].iloc[0]
    structure_type = data["STRUCTURE"].iloc[0]
    # Drop 'STRUCTURE' and 'STRUCTURE_ID' columns from DataFrame
    df_csv = data.drop(["STRUCTURE", "STRUCTURE_ID"], axis=1)

    if structure_type == "DataStructure".lower():
        urn = (
            "urn:sdmx:org.sdmx.infomodel.datastructure."
            f"DataStructure={structure_id}"
        )
    elif structure_type == "DataFlow".lower():
        urn = (
            "urn:sdmx:org.sdmx.infomodel.datastructure."
            f"DataFlow={structure_id}"
        )
    elif structure_type == "dataprovision":
        urn = (
            f"urn:sdmx:org.sdmx.infomodel.registry."
            f"ProvisionAgreement={structure_id}"
        )
    else:
        raise Invalid(
            "Invalid value on STRUCTURE column",
            "Invalid SDMX-CSV 2.0 file. "
            "Check the docs for the proper values on STRUCTURE column.",
        )
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
        action=action,
    )


def read(infile: str) -> Dict[str, PandasDataset]:
    """Reads csv file and returns a payload dictionary.

    Args:
        infile: Path to file, str.

    Returns:
        payload: dict.

    Raises:
        Invalid: If it is an invalid CSV file.
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
        raise Invalid(
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

    # Grouping columns to separate datasets
    grouping_columns = ["STRUCTURE", "STRUCTURE_ID"]
    # Separate SDMX-CSV in different datasets per Structure ID
    list_df = [data for _, data in df_csv.groupby(grouping_columns)]

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
