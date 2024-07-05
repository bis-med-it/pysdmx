"""SDMX 2.0 CSV reader module."""
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


def generate_dataset_from_sdmx_csv(data: pd.DataFrame, sdmx_csv_version):
    # Extract Structure type and structure id

    if sdmx_csv_version == 2:
        if 'ACTION' in data.columns:
            # Drop 'ACTION' column from DataFrame
            data = data.drop(['ACTION'], axis=1)
        # For SDMX-CSV version 2, use 'STRUCTURE_ID'
        # column as the structure id and 'STRUCTURE' as the structure type
        structure_id = data['STRUCTURE_ID'].iloc[0]
        structure_type = data['STRUCTURE'].iloc[0]
        # Drop 'STRUCTURE' and 'STRUCTURE_ID' columns from DataFrame
        df_csv = data.drop(['STRUCTURE', 'STRUCTURE_ID'], axis=1)

    # Return a Dataset object with the extracted information
    return Dataset(unique_id=structure_id, structure_type=structure_type,
                   data=df_csv, attached_attributes={})


def read_csv(infile: str):
    # Get Dataframe from CSV file
    df_csv = pd.read_csv(infile)
    # Drop empty columns
    df_csv = df_csv.dropna(axis=1, how='all')

    # Determine SDMX-CSV version based on column names
    if 'STRUCTURE' in df_csv.columns and 'STRUCTURE_ID' in df_csv.columns:
        version = 2
    else:
        # Raise an exception if the CSV file is not in SDMX-CSV format
        raise Exception('Invalid CSV file, only SDMX-CSV is allowed')

    # Convert all columns to strings
    df_csv = df_csv.astype('str')
    # Check if any column headers contain ':', indicating mode, label or text
    mode_label_text = any([':' in x for x in df_csv.columns])

    # Determine the id column based on the SDMX-CSV version
    if version == 2:
        id_column = 'STRUCTURE_ID'

    # If mode, label or text is present, modify the DataFrame
    if mode_label_text:
        # Split the ID column to remove mode, label or text
        df_csv[id_column] = df_csv[id_column].map(lambda x: x.split(': ')[0])
        # Split the other columns to remove mode, label, or text
        sequence = 1 if version == 1 else 3
        for x in df_csv.columns[sequence:]:
            df_csv[x.split(':')[0]] = df_csv[x].map(
                lambda x: x.split(': ', 2)[0],
                na_action='ignore')
            # Delete the original columns
            del df_csv[x]

    # Separate SDMX-CSV in different datasets per Structure ID
    list_df = [data for _, data in df_csv.groupby(id_column)]

    # Create a payload dictionary to store datasets with the
    # different unique_ids as keys
    payload = {}
    for df in list_df:
        # Generate a dataset from each subset of the DataFrame
        dataset = generate_dataset_from_sdmx_csv(data=df,
                                                 sdmx_csv_version=version)
        # Add the dataset to the payload dictionary
        payload[dataset.unique_id] = dataset

    # Return the payload generated
    return payload

