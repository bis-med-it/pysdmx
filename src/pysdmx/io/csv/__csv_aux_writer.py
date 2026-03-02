from copy import copy
from typing import List, Literal, Optional, Sequence

import pandas as pd

from pysdmx.io._pd_utils import (
    transform_dataframe_for_writing,
    validate_schema_exists,
)
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Schema
from pysdmx.model.dataflow import Component, Role
from pysdmx.model.dataset import ActionType
from pysdmx.toolkit.pd._data_utils import format_labels, get_codes

SDMX_CSV_ACTION_MAPPER = {
    ActionType.Append: "A",
    ActionType.Replace: "R",
    ActionType.Information: "I",
    ActionType.Delete: "D",
}


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
    obs_values = ".".join(
        str(df[k].iloc[0]) for k in obs_codes if k in df.columns
    )
    series_values = ".".join(
        str(df[k].iloc[0]) for k in series_codes if k in df.columns
    )
    if keys == "obs":
        df.insert(0, "OBS_KEYS", obs_values)
    elif keys == "series":
        df.insert(0, "SERIES_KEYS", series_values)
    else:
        df.insert(0, "OBS_KEYS", obs_values)
        df.insert(0, "SERIES_KEYS", series_values)


def _reorder_columns(
    df: pd.DataFrame,
    components: Sequence[Component],
) -> pd.DataFrame:
    """Reorder DataFrame columns following SDMX-CSV conventions.

    Columns are ordered as: dimensions, measures, attributes.
    Any columns not in the schema are appended at the end.

    Args:
        df: The DataFrame to reorder.
        components: The schema components.

    Returns:
        The DataFrame with reordered columns.
    """
    role_order = {Role.DIMENSION: 0, Role.MEASURE: 1, Role.ATTRIBUTE: 2}
    schema_cols: list[str] = []
    for role_val in sorted(role_order, key=role_order.get):  # type: ignore[arg-type]
        schema_cols.extend(
            comp.id
            for comp in components
            if comp.role == role_val and comp.id in df.columns
        )
    remaining = [c for c in df.columns if c not in schema_cols]
    return df[schema_cols + remaining]


def _write_csv_2_aux(
    datasets: Sequence[PandasDataset],
    labels: Optional[Literal["name", "id", "both"]] = None,
    time_format: Optional[Literal["original", "normalized"]] = None,
    keys: Optional[Literal["obs", "series", "both"]] = None,
    references_21: bool = False,
) -> List[pd.DataFrame]:
    dataframes = []
    for dataset in datasets:
        # Validate that the dataset has a Schema defined
        schema = validate_schema_exists(dataset)

        # Create a copy and apply null value transformation
        df: pd.DataFrame = copy(dataset.data)
        df = transform_dataframe_for_writing(df, schema)

        structure_ref, unique_id = dataset.short_urn.split("=", maxsplit=1)

        # Add additional attributes to the dataset
        for k, v in dataset.attributes.items():
            df[k] = v

        # Reorder columns: dimensions, measures, attributes
        df = _reorder_columns(df, schema.components)

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
        if keys is not None:
            __write_keys(df, keys, schema)
        if labels is not None:
            format_labels(df, labels, schema.components)
            df.insert(0, "STRUCTURE", structure_ref)
            df.insert(
                1,
                "STRUCTURE_ID",
                f"{unique_id}:{schema.name}"
                if labels == "both"
                else unique_id,
            )
            action_position = 2
            if labels == "name":
                action_position += 1
                df.insert(2, "STRUCTURE_NAME", schema.name)
            df.insert(action_position, "ACTION", action_value)
        else:
            df.insert(0, "STRUCTURE", structure_ref)
            df.insert(1, "STRUCTURE_ID", unique_id)
            df.insert(2, "ACTION", action_value)
        dataframes.append(df)
    return dataframes
