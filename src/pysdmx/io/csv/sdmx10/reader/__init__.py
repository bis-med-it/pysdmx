"""SDMX 1.0 CSV reader module."""
from io import StringIO

import pandas as pd

from pysdmx.model.dataset import Dataset


def __generate_dataset_from_sdmx_csv(data: pd.DataFrame):
    # Extract Structure type and structure id

    # For SDMX-CSV version 1, use 'DATAFLOW' column as the structure id
    structure_id = data['DATAFLOW'].iloc[0]
    # Structure type will be "dataflow" in both versions
    structure_type = 'dataflow'
    # Drop 'DATAFLOW' column from DataFrame
    df_csv = data.drop(['DATAFLOW'], axis=1)

    # Return a Dataset object with the extracted information
    return Dataset(unique_id=structure_id, structure_type=structure_type,
                   data=df_csv, attached_attributes={})


def read(infile: str):
    # Get Dataframe from CSV file
    df_csv = pd.read_csv(StringIO(infile))
    # Drop empty columns
    df_csv = df_csv.dropna(axis=1, how='all')

    # Determine SDMX-CSV version based on column names
    if 'DATAFLOW' not in df_csv.columns:
        # Raise an exception if the CSV file is not in SDMX-CSV format
        raise Exception('Invalid CSV file, only SDMX-CSV is allowed')

    # Convert all columns to strings
    df_csv = df_csv.astype('str')
    # Check if any column headers contain ':', indicating mode, label or text
    mode_label_text = any([':' in x for x in df_csv.columns])

    # Determine the id column based on the SDMX-CSV version
    id_column = 'DATAFLOW'

    # If mode, label or text is present, modify the DataFrame
    if mode_label_text:
        # Split the ID column to remove mode, label or text
        df_csv[id_column] = df_csv[id_column].map(lambda x: x.split(': ')[0])
        # Split the other columns to remove mode, label, or text
        sequence = 1
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
        dataset = __generate_dataset_from_sdmx_csv(data=df)

        # Add the dataset to the payload dictionary
        payload[dataset.unique_id] = dataset

    # Return the payload generated
    return payload
