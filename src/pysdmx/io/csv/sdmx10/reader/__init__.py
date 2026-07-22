"""SDMX 1.0 CSV reader module."""

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
    if "DATAFLOW" not in df_csv.columns:
        # Raise an exception if the CSV file is not in SDMX-CSV format
        raise Invalid(
            "Only SDMX-CSV 1.0 is allowed",
            "Invalid SDMX-CSV 1.0 file. "
            "Check the docs for the proper structure on content.",
        )

    # Convert all columns to strings
    df_csv = df_csv.astype(str).replace({"nan": "NaN", "<NA>": "NaN"})
    # A ': ' in a header marks a labelled column, since labels are
    # written with a ': ' separator
    mode_label_text = any(": " in x for x in df_csv.columns)

    # Determine the id column based on the SDMX-CSV version
    id_column = "DATAFLOW"

    # If mode, label or text is present, modify the DataFrame
    if mode_label_text:
        # Strip the label from every labelled column (identified by a ': ' in
        # its header). Labels use a ': ' (colon-space) separator and codes
        # never contain spaces, so a bare ':' inside a value (e.g. a full
        # datetime) is preserved. The structure id label is stripped later,
        # in __generate_dataset_from_sdmx_csv.
        for x in [col for col in df_csv.columns if ": " in col]:
            df_csv[x.split(": ")[0]] = df_csv[x].map(
                lambda x: x.split(": ", 2)[0], na_action="ignore"
            )
            # Delete the original columns
            del df_csv[x]

    # Separate SDMX-CSV in different datasets per Structure ID
    list_df = [data for _, data in df_csv.groupby(id_column)]

    # Create a payload dictionary to store datasets with the
    # different unique_ids as keys
    payload = []
    for df in list_df:
        # Generate a dataset from each subset of the DataFrame
        dataset = __generate_dataset_from_sdmx_csv(data=df)

        # Add the dataset to the payload dictionary
        payload.append(dataset)

    # Return the payload generated
    return payload
