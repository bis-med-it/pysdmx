"""SDMX 2.0 CSV writer module."""

from pathlib import Path
from typing import Literal, Optional, Sequence, Union

import pandas as pd

from pysdmx.io.csv.__csv_aux_writer import (
    _write_csv_2_aux,
)
from pysdmx.io.pd import PandasDataset


def write(
    datasets: Sequence[PandasDataset],
    labels: Optional[Literal["name", "id", "both"]] = None,
    time_format: Optional[Literal["original", "normalized"]] = None,
    keys: Optional[Literal["obs", "series", "both"]] = None,
    output_path: Optional[Union[str, Path]] = None,
) -> Optional[str]:
    """Write data to SDMX-CSV 2.0 format.

    Args:
        datasets: List of datasets to write.
          Must have the same components.
        labels: How to write the name of the columns.
            If None, only the IDs are written.
            if "id", the names are written as ID only.
            if "name", a colum called "STRUCTURE_NAME" is
            added after struture ID.
            If "both", the names are witten as id:Name.
        time_format: How to write the time period.
            If None, the time period is not modified.
            If "original", the time period is written as it
            is in the dataset.
            "normalized" is not implemented yet.
        keys: to write or not the keys columns
            If None, no keys are written.
            If "obs", the keys are write as a single
            column called "OBS_KEY".
            If "series", the keys are write as a single
            column called "SERIES_KEY".
            If "both", the keys are write as two columns:
            "OBS_KEY" and "SERIES_KEY".
        output_path: Path to write the data to.
          If None, the data is returned as a string.

    Returns:
        SDMX CSV data as a string, if output_path is None.
    """
    # Link to pandas.to_csv documentation on sphinx:
    # https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.to_csv.html

    dataframes = _write_csv_2_aux(
        datasets,
        labels,
        time_format,
        keys,
    )

    all_data = pd.concat(dataframes, ignore_index=True, axis=0)

    all_data = all_data.astype(str)

    # If the output path is an empty string we use None
    output_path = (
        None
        if isinstance(output_path, str) and output_path == ""
        else output_path
    )

    # Convert the dataset into a csv file
    return all_data.to_csv(output_path, index=False, header=True)
