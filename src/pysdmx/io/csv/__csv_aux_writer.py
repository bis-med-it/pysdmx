from copy import copy
from typing import Dict, List, Literal, Optional, Sequence, Tuple

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

_NULL_STRINGS = frozenset(("", "nan", "None", "#N/A", "NaN"))

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
    df: pd.DataFrame,
    keys: Literal["obs", "series", "both"],
    schema: Schema,
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


def __generate_partial_key_df(
    df: pd.DataFrame,
    schema: Schema,
) -> pd.DataFrame:
    """Generate partial key rows from observation data.

    Transforms a flat DataFrame into one where series-level
    and group-level attributes appear on their own rows with
    only their attachment dimensions filled, per SDMX-CSV 2.x
    section 1.3.

    Args:
        df: The DataFrame with observation data.
        schema: The schema describing the data structure.

    Returns:
        A new DataFrame with partial key rows prepended
        before observation rows.
    """
    partial_attr_list: List[Tuple[str, List[str]]] = []
    for att in schema.components.attributes:
        level = att.attachment_level
        if level is None or level in ("O", "D") or att.id not in df.columns:
            continue
        dims = level.split(",")
        partial_attr_list.append((att.id, dims))

    if not partial_attr_list:
        return df

    all_columns = list(df.columns)
    partial_attr_ids = {pa[0] for pa in partial_attr_list}
    partial_rows: List[Dict[str, object]] = []

    for attr_id, pa_dims in partial_attr_list:
        cols = pa_dims + [attr_id]
        sub = df[cols].drop_duplicates().dropna(subset=[attr_id])
        sub = sub[~sub[attr_id].astype(str).isin(_NULL_STRINGS)]
        for rec in sub.to_dict(orient="records"):
            row: Dict[str, object] = dict.fromkeys(all_columns, "")
            for d in pa_dims:
                row[d] = rec[d]
            row[attr_id] = rec[attr_id]
            partial_rows.append(row)

    obs_df = df.copy()
    for attr_id in partial_attr_ids:
        obs_df[attr_id] = ""

    partial_df = pd.DataFrame(partial_rows, columns=all_columns)
    return pd.concat([partial_df, obs_df], ignore_index=True)


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


def __insert_structural_columns(
    df: pd.DataFrame,
    dataset: PandasDataset,
    structure_ref: str,
    unique_id: str,
    action_value: str,
    labels: Optional[Literal["name", "id", "both"]],
) -> None:
    """Insert STRUCTURE, STRUCTURE_ID, and ACTION columns.

    Args:
        df: The DataFrame to modify.
        dataset: The dataset being written.
        structure_ref: The structure reference type.
        unique_id: The unique identifier.
        action_value: The action code.
        labels: The label format option.
    """
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
            df.insert(
                2,
                "STRUCTURE_NAME",
                dataset.structure.name,
            )
        df.insert(action_position, "ACTION", action_value)
    else:
        df.insert(0, "STRUCTURE", structure_ref)
        df.insert(1, "STRUCTURE_ID", unique_id)
        df.insert(2, "ACTION", action_value)


def _write_csv_2_aux(
    datasets: Sequence[PandasDataset],
    labels: Optional[Literal["name", "id", "both"]] = None,
    time_format: Optional[Literal["original", "normalized"]] = None,
    keys: Optional[Literal["obs", "series", "both"]] = None,
    references_21: bool = False,
    partial_keys: bool = False,
) -> List[pd.DataFrame]:
    """Write datasets to SDMX-CSV 2.x format.

    Args:
        datasets: List of datasets to write.
        labels: How to write the name of the columns.
        time_format: How to write the time period.
        keys: to write or not the keys columns.
        references_21: Whether to use SDMX 2.1 references.
        partial_keys: Whether to write partial key rows
            for series-level and group-level attributes.

    Returns:
        List of DataFrames ready for CSV output.

    Raises:
        Invalid: If partial_keys is True but the dataset
            structure is not a Schema.
    """
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

        if partial_keys:
            df = __generate_partial_key_df(df, schema)

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
        __insert_structural_columns(
            df, dataset, structure_ref, unique_id, action_value, labels
        )
        dataframes.append(df)
    return dataframes
