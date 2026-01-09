from copy import copy
from typing import List, Literal, Optional, Sequence

import pandas as pd

from pysdmx.io._pd_utils import _validate_schema_exists
from pysdmx.io.pd import PandasDataset
from pysdmx.model import Schema
from pysdmx.model.dataset import ActionType
from pysdmx.toolkit.pd._data_utils import format_labels, get_codes

SDMX_CSV_ACTION_MAPPER = {
    ActionType.Append: "A",
    ActionType.Replace: "R",
    ActionType.Information: "I",
    ActionType.Delete: "D",
}


def _csv_prepare_df(dataset: PandasDataset) -> pd.DataFrame:
    schema = _validate_schema_exists(dataset)
    df: pd.DataFrame = copy(dataset.data)

    for k, v in dataset.attributes.items():
        df[k] = v

    for comp in schema.components:
        if comp.required and comp.id not in df.columns:
            df[comp.id] = pd.NA

    optional_attrs = {
        comp.id for comp in schema.components.attributes if not comp.required
    }
    for attr_id in optional_attrs:
        if attr_id in df.columns:
            col_values = df[attr_id]
            if (
                col_values.isna().all()
                or (col_values.astype(str).str.strip() == "").all()
            ):
                df = df.drop(columns=[attr_id])

    return df


def _csv_structure_ref_and_id(short_urn: str) -> tuple[str, str]:
    structure_ref, unique_id = short_urn.split("=", maxsplit=1)
    if structure_ref in ["DataStructure", "Dataflow"]:
        structure_ref = structure_ref.lower()
    else:
        structure_ref = "dataprovision"
    return structure_ref, unique_id


def _csv_determine_action(dataset: PandasDataset, references_21: bool) -> str:
    if references_21 and dataset.action in [
        ActionType.Information,
        ActionType.Append,
    ]:
        return "M"
    return SDMX_CSV_ACTION_MAPPER[dataset.action]


def _csv_insert_labels_action(
    df: pd.DataFrame,
    dataset: PandasDataset,
    structure_ref: str,
    unique_id: str,
    action_value: str,
    labels: Literal["name", "id", "both"],
) -> None:
    schema = _validate_schema_exists(dataset)

    format_labels(df, labels, schema.components)
    df.insert(0, "STRUCTURE", structure_ref)
    structure_name = schema.name
    if labels == "both":
        structure_id_value = f"{unique_id}:{structure_name}"
    else:
        structure_id_value = unique_id
    df.insert(1, "STRUCTURE_ID", structure_id_value)
    action_position = 2
    if labels == "name":
        action_position += 1
        df.insert(2, "STRUCTURE_NAME", schema.name)
    df.insert(action_position, "ACTION", action_value)


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
    dataframes: List[pd.DataFrame] = []
    for dataset in datasets:
        df = _csv_prepare_df(dataset)

        structure_ref, unique_id = _csv_structure_ref_and_id(dataset.short_urn)

        action_value = _csv_determine_action(dataset, references_21)

        if time_format is not None and time_format != "original":
            __write_time_period(df, time_format)
        if keys is not None and isinstance(dataset.structure, Schema):
            __write_keys(df, keys, dataset.structure)
        if labels is not None and isinstance(dataset.structure, Schema):
            _csv_insert_labels_action(
                df, dataset, structure_ref, unique_id, action_value, labels
            )
        else:
            df.insert(0, "STRUCTURE", structure_ref)
            df.insert(1, "STRUCTURE_ID", unique_id)
            df.insert(2, "ACTION", action_value)
        dataframes.append(df)

    return dataframes
