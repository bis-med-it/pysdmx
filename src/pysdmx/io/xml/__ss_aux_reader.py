"""SDMX XML StructureSpecificData reader aux module."""

import itertools
from typing import Any, Dict

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
            for j in data[OBS]:
                test_list.append({**keys, **j})
        else:
            test_list.append(keys)
        test_list, df = __process_df(test_list, df)

    test_list, df = __process_df(test_list, df, is_end=True)

    return df


def _reading_group_data(dataset: Dict[str, Any]) -> pd.DataFrame:
    # Structure Specific Group Data
    test_list = []
    df = None
    dataset[GROUP] = add_list(dataset[GROUP])
    for data in dataset[GROUP]:
        test_list.append(dict(data.items()))
        test_list, df = __process_df(test_list, df)
    test_list, df = __process_df(test_list, df, is_end=True)

    cols_to_delete = [x for x in df.columns if ":type" in x]
    for x in cols_to_delete:
        del df[x]

    df = df.drop_duplicates(keep="first").reset_index(drop=True)

    return df


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
            df_group = _reading_group_data(dataset)
            common_columns = list(
                set(df.columns).intersection(set(df_group.columns))
            )
            df = pd.merge(df, df_group, on=common_columns, how="left")
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
