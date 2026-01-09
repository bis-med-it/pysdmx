"""SDMX 1.0 CSV writer module."""

from pathlib import Path
from typing import Literal, Optional, Sequence, Union

import pandas as pd

from pysdmx.io._pd_utils import _validate_schema_exists
from pysdmx.io.csv.__csv_aux_writer import __write_time_period, _csv_prepare_df
from pysdmx.io.pd import PandasDataset
from pysdmx.toolkit.pd._data_utils import format_labels


def write(
    datasets: Sequence[PandasDataset],
    labels: Optional[Literal["id", "both"]] = None,
    time_format: Optional[Literal["original", "normalized"]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Optional[str]:
    """Write data to SDMX-CSV 1.0 format.

    Args:
        datasets: List of datasets to write.
          Must have the same components.
        output_path: Path to write the data to.
          If None, the data is returned as a string.
        labels: How to write the name of the columns.
            If None, only the IDs are written.
            if "id", the names are written as ID only.
            If "both", the names are witten as id:Name.
        time_format: How to write the time period.
            If None, the time period is not modified.
            If "original", the time period is written as it
            is in the dataset.
            "Normalized" is not implemented yet.

    Returns:
        SDMX CSV data as a string, if output_path is None.
    """
    # Link to pandas.to_csv documentation on sphinx:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html

    # Create a copy of the dataset
    dataframes = []
    for dataset in datasets:
        df = _csv_prepare_df(dataset)
        schema = _validate_schema_exists(dataset)

        structure_id = dataset.short_urn.split("=")[1]
        if time_format is not None and time_format != "original":
            __write_time_period(df, time_format)
        if labels is not None:
            format_labels(df, labels, schema.components)
            if labels == "id":
                df.insert(0, "DATAFLOW", structure_id)
            else:
                df.insert(0, "DATAFLOW", f"{structure_id}:{schema.name}")
        else:
            df.insert(0, "DATAFLOW", structure_id)

        dataframes.append(df)

    # Concatenate the dataframes
    all_data = pd.concat(dataframes, ignore_index=True, axis=0)

    # If the output path is an empty string we use None
    output_path = (
        None
        if isinstance(output_path, str) and output_path == ""
        else output_path
    )

    # Return the SDMX CSV data as a string
    return all_data.to_csv(output_path, index=False, header=True)
