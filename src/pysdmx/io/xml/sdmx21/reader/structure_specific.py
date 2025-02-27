"""SDMX 2.1 XML StructureSpecificData reader module."""

import itertools
from typing import Any, Dict, Sequence

import numpy as np
import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx21.__tokens import (
    EXCLUDED_ATTRIBUTES,
    GROUP,
    OBS,
    SERIES,
    STR_REF,
    STR_SPE,
)
from pysdmx.io.xml.sdmx21.reader.__data_aux import (
    __process_df,
    get_data_objects,
)
from pysdmx.io.xml.sdmx21.reader.__parse_xml import parse_xml
from pysdmx.io.xml.utils import add_list
from pysdmx.model.dataset import ActionType


def __reading_str_series(dataset: Dict[str, Any]) -> pd.DataFrame:
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


def __reading_group_data(dataset: Dict[str, Any]) -> pd.DataFrame:
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


def __get_at_att_str(dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Gets the elements of the dataset if it is Structure Specific Data."""
    return {k: dataset[k] for k in dataset if k not in EXCLUDED_ATTRIBUTES}


def __parse_structure_specific_data(
    dataset: Dict[str, Any], structure_info: Dict[str, Any]
) -> PandasDataset:
    attached_attributes = __get_at_att_str(dataset)

    df = pd.DataFrame()

    # Parsing data
    if SERIES in dataset:
        # Structure Specific Series
        df = __reading_str_series(dataset)
        if GROUP in dataset:
            df_group = __reading_group_data(dataset)
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


def read(input_str: str, validate: bool = True) -> Sequence[PandasDataset]:
    """Reads an SDMX-ML 2.1 Generic file and returns a Sequence of Datasets.

    Args:
        input_str: SDMX-ML data to read.
        validate: If True, the XML data will be validated against the XSD.
    """
    dict_info = parse_xml(input_str, validate=validate)
    if STR_SPE not in dict_info:
        raise Invalid(
            "This SDMX document is not an SDMX-ML 2.1 StructureSpecificData."
        )
    dataset_info, str_info = get_data_objects(dict_info[STR_SPE])
    datasets = []
    for dataset in dataset_info:
        ds = __parse_structure_specific_data(
            dataset, str_info[dataset[STR_REF]]
        )
        datasets.append(ds)
    return datasets
