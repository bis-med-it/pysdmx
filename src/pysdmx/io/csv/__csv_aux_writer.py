from copy import copy
from typing import List, Literal, Optional, Sequence

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Schema
from pysdmx.model.dataset import ActionType
from pysdmx.toolkit.pd._data_utils import (
    fill_na_values,
    format_labels,
    get_codes,
)

SDMX_CSV_ACTION_MAPPER = {
    ActionType.Append: "A",
    ActionType.Replace: "R",
    ActionType.Information: "I",
    ActionType.Delete: "D",
}


def _validate_schema_exists(dataset: PandasDataset) -> None:
    """Validates that the dataset has a Schema defined."""
    if not isinstance(dataset.structure, Schema):
        raise Invalid(
            "Dataset Structure is not a Schema. Cannot perform operation."
        )


def __write_time_period(df: pd.DataFrame, time_format: str) -> None:
    # TODO: Correct handle of normalized time format
    raise NotImplementedError("Normalized time format is not implemented yet.")


def __write_keys(
    df: pd.DataFrame, keys: Literal["obs", "series", "both"], schema: Schema
) -> None:
    """Writes the keys to the DataFrame.

    Args:
        df: The DataFrame to write the keys to.
        keys: to write or not the keys columns
            If None, no keys are written.
            If "obs", the keys are write as a single
            column called "OBS_KEY".
            If "series", the keys are write as a single
            column called "SERIES_KEY".
            If "both", the keys are write as two columns:
            "OBS_KEY" and "SERIES_KEY".
        schema: The schema to get the keys
    """
    series_codes, obs_codes, group_codes = get_codes(
        dimension_code="", structure=schema, data=df
    )
    del obs_codes[0]
    obs_parts = []
    series_parts = []
    for k, v in df.items():
        value = v.iloc[0]
        if k in obs_codes:
            obs_parts.append(str(value))
        if k in series_codes:
            series_parts.append(str(value))
    obs_values = ".".join(obs_parts)
    series_values = ".".join(series_parts)
    if keys == "obs":
        df.insert(0, "OBS_KEYS", obs_values)
    elif keys == "series":
        df.insert(0, "SERIES_KEYS", series_values)
    else:
        df.insert(0, "OBS_KEYS", obs_values)
        df.insert(0, "SERIES_KEYS", series_values)


def _write_csv_2_aux(
    datasets: Sequence[PandasDataset],
    labels: Optional[Literal["name", "id", "both"]] = None,
    time_format: Optional[Literal["original", "normalized"]] = None,
    keys: Optional[Literal["obs", "series", "both"]] = None,
    references_21: bool = False,
) -> List[pd.DataFrame]:
    dataframes = []
    for dataset in datasets:
        _validate_schema_exists(dataset)
        # Create a copy of the dataset
        df: pd.DataFrame = copy(dataset.data)
        df = fill_na_values(df, dataset.structure)
        structure_ref, unique_id = dataset.short_urn.split("=", maxsplit=1)

        # Add additional attributes to the dataset
        for k, v in dataset.attributes.items():
            df[k] = v

        if structure_ref in ["DataStructure", "Dataflow"]:
            structure_ref = structure_ref.lower()
        else:
            structure_ref = "dataprovision"

        if references_21 and dataset.action in [
            ActionType.Information,
            ActionType.Append,
        ]:
            action_value = "M"
        else:
            action_value = SDMX_CSV_ACTION_MAPPER[dataset.action]

        if time_format is not None and time_format != "original":
            __write_time_period(df, time_format)
        if keys is not None and isinstance(dataset.structure, Schema):
            __write_keys(df, keys, dataset.structure)
        if labels is not None and isinstance(dataset.structure, Schema):
            format_labels(df, labels, dataset.structure.components)
            df.insert(0, "STRUCTURE", structure_ref)
            df.insert(
                1,
                "STRUCTURE_ID",
                f"{unique_id}:{dataset.structure.name}"
                if labels == "both"
                else unique_id,
            )
            action_position = 2
            if labels == "name":
                action_position += 1
                df.insert(2, "STRUCTURE_NAME", dataset.structure.name)
            df.insert(action_position, "ACTION", action_value)
        else:
            df.insert(0, "STRUCTURE", structure_ref)
            df.insert(1, "STRUCTURE_ID", unique_id)
            df.insert(2, "ACTION", action_value)
        dataframes.append(df)
    return dataframes
