"""SDMX XML StructureSpecificData reader aux module."""

import itertools
from typing import Any, Dict, List

import numpy as np
import pandas as pd

from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.__data_aux import (
    __process_df,
)
from pysdmx.io.xml.__tokens import (
    EXCLUDED_ATTRIBUTES,
    GROUP,
    OBS,
    SERIES,
)
from pysdmx.io.xml.utils import add_list
from pysdmx.model.dataset import ActionType


def _reading_str_series(dataset: Dict[str, Any]) -> pd.DataFrame:
    # Structure Specific Series
    test_list = []
    df = None
    dataset[SERIES] = add_list(dataset[SERIES])
    for data in dataset[SERIES]:
        keys = dict(itertools.islice(data.items(), len(data)))
        if OBS in data:
            del keys[OBS]
            data[OBS] = add_list(data[OBS])
            test_list.extend([{**keys, **j} for j in data[OBS]])
        else:
            test_list.append(keys)
        test_list, df = __process_df(test_list, df)

    test_list, df = __process_df(test_list, df, is_end=True)

    return df


def _reading_group_data(dataset: Dict[str, Any]) -> List[pd.DataFrame]:
    # Structure Specific Group Data
    group_dfs = []
    dataset[GROUP] = add_list(dataset[GROUP])
    for data in dataset[GROUP]:
        group_dict = dict(data.items())
        group_df = pd.DataFrame([group_dict])

        # Remove :type columns
        cols_to_delete = [x for x in group_df.columns if ":type" in x]
        for x in cols_to_delete:
            del group_df[x]

        group_dfs.append(group_df)

    return group_dfs


def _get_at_att_str(dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Gets the elements of the dataset if it is Structure Specific Data."""
    return {k: dataset[k] for k in dataset if k not in EXCLUDED_ATTRIBUTES}


def _parse_structure_specific_data(
    dataset: Dict[str, Any], structure_info: Dict[str, Any]
) -> PandasDataset:
    attached_attributes = _get_at_att_str(dataset)

    df = pd.DataFrame()

    # Parsing data
    if SERIES in dataset:
        # Structure Specific Series
        df = _reading_str_series(dataset)
        if GROUP in dataset:
            group_dfs = _reading_group_data(dataset)
            original_columns = df.columns.tolist()
            for group_df in group_dfs:
                # Find non-NaN columns in this group
                non_nan_cols = [
                    col
                    for col in group_df.columns
                    if not group_df[col].isna().all()
                ]

                # Merge keys are intersection of original and non-NaN cols
                merge_cols = list(
                    set(original_columns).intersection(set(non_nan_cols))
                )

                if merge_cols:
                    group_df = group_df.drop_duplicates(
                        merge_cols, keep="first"
                    )
                    df = pd.merge(
                        df,
                        group_df,
                        on=merge_cols,
                        how="left",
                        suffixes=("", "_drop"),
                    )
                    for col in list(df.columns):
                        if col.endswith("_drop"):
                            original = col[:-5]
                            df[original] = df[original].fillna(df[col])
                            df.drop(col, axis=1, inplace=True)
    elif OBS in dataset:
        dataset[OBS] = add_list(dataset[OBS])
        # Structure Specific All dimensions
        df = pd.DataFrame(dataset[OBS]).replace(np.nan, "")

    urn = f"{structure_info['structure_type']}={structure_info['unique_id']}"
    action = dataset.get("action", "Information")
    action = ActionType(action)

    return PandasDataset(
        structure=urn, attributes=attached_attributes, data=df, action=action
    )
