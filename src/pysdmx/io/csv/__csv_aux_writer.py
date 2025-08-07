from copy import copy
from typing import List, Literal, Optional, Sequence

import pandas as pd

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__write_data_aux import get_codes
from pysdmx.model import Schema
from pysdmx.model.dataset import ActionType

SDMX_CSV_ACTION_MAPPER = {
    ActionType.Append: "A",
    ActionType.Replace: "R",
    ActionType.Information: "I",
    ActionType.Delete: "D",
    ActionType.Merge: "M",
}


def __write_labels(
    df: pd.DataFrame,
    labels: Literal["name", "both"],
    schema: Schema,
) -> None:
    """Writes the labels to the DataFrame.

    Args:
        df: The DataFrame to write the labels to.
        labels: The label type to write.
            if "id" the id of the data is written.
            if "name" the name of the data is written.
            if "both" a string id:name is written.
        schema: The schema to use for the labels
        to get the names
    """
    data = schema.components.data
    if labels == "name":
        for k in df.columns:
            for component in data:
                if component.id == k:
                    df.rename(
                        columns={k: component.concept.name},  # type: ignore[union-attr]
                        inplace=True,
                    )
    else:
        for k in df.columns:
            v = df[k]
            for component in data:
                if component.id == k:
                    df[f"{k}:{component.concept.name}"] = v.apply(  # type: ignore[union-attr]
                        lambda x: f"{x}:{x}"
                    )
                    df.drop(columns=[k], inplace=True)


def __write_time_period(df: pd.DataFrame, time_format: str) -> None:
    if "TIME_PERIOD" not in df.columns or "FREQ" not in df.columns:
        return
    freq = df["FREQ"]
    year = df["TIME_PERIOD"]

    df["TIME_PERIOD"] = year

    df.loc[(freq == "A"), "TIME_PERIOD"] = year + "-12-31"


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
    series_codes, obs_codes = get_codes(
        dimension_code="", structure=schema, data=df
    )
    del obs_codes[0]
    obs_parts = []
    series_parts = []
    for k, v in df.items():
        value = v.iloc[0]
        if k in obs_codes:
            obs_parts.append(value)
        if k in series_codes:
            series_parts.append(value)
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
        # Create a copy of the dataset
        df: pd.DataFrame = copy(dataset.data)
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
            action_value = SDMX_CSV_ACTION_MAPPER[ActionType.Merge]
        else:
            action_value = SDMX_CSV_ACTION_MAPPER[dataset.action]

        if time_format is not None and time_format != "original":
            __write_time_period(df, time_format)
        if keys is not None and isinstance(dataset.structure, Schema):
            __write_keys(df, keys, dataset.structure)
        if (
            labels is not None
            and isinstance(dataset.structure, Schema)
            and labels != "id"
        ):
            __write_labels(df, labels, dataset.structure)
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
