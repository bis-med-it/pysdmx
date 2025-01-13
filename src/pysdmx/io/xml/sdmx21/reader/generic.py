"""SDMX 2.1 XML Generic Data reader module."""

from typing import Any, Dict, Sequence

import pandas as pd

from pysdmx.errors import Invalid
from pysdmx.io.pd import PandasDataset
from pysdmx.io.xml.sdmx21.__tokens import (
    ATTRIBUTES,
    GENERIC,
    ID,
    OBS,
    OBS_DIM,
    OBSKEY,
    OBSVALUE,
    SERIES,
    SERIESKEY,
    STRREF,
    VALUE,
)
from pysdmx.io.xml.sdmx21.reader.__data_aux import (
    __process_df,
    get_data_objects,
)
from pysdmx.io.xml.sdmx21.reader.__parse_xml import parse_xml
from pysdmx.io.xml.utils import add_list


def __get_element_to_list(data: Dict[str, Any], mode: Any) -> Dict[str, Any]:
    obs = {}
    data[mode][VALUE] = add_list(data[mode][VALUE])
    for k in data[mode][VALUE]:
        obs[k[ID]] = k[VALUE.lower()]
    return obs


def __reading_generic_series(dataset: Dict[str, Any]) -> pd.DataFrame:
    # Generic Series
    test_list = []
    df = None
    dataset[SERIES] = add_list(dataset[SERIES])
    for series in dataset[SERIES]:
        keys = {}
        # Series Keys
        series[SERIESKEY][VALUE] = add_list(series[SERIESKEY][VALUE])
        for v in series[SERIESKEY][VALUE]:
            keys[v[ID]] = v[VALUE.lower()]
        if ATTRIBUTES in series:
            series[ATTRIBUTES][VALUE] = add_list(series[ATTRIBUTES][VALUE])
            for v in series[ATTRIBUTES][VALUE]:
                keys[v[ID]] = v[VALUE.lower()]
        if OBS in series:
            series[OBS] = add_list(series[OBS])

            for data in series[OBS]:
                obs = {
                    OBS_DIM: data[OBS_DIM][VALUE.lower()],
                    OBSVALUE.upper(): data[OBSVALUE][VALUE.lower()],
                }
                if ATTRIBUTES in data:
                    obs = {
                        **obs,
                        **__get_element_to_list(data, mode=ATTRIBUTES),
                    }
                test_list.append({**keys, **obs})
        else:
            test_list.append(keys)
        test_list, df = __process_df(test_list, df)

    test_list, df = __process_df(test_list, df, is_end=True)

    return df


def __reading_generic_all(dataset: Dict[str, Any]) -> pd.DataFrame:
    # Generic All Dimensions
    test_list = []
    df = None
    dataset[OBS] = add_list(dataset[OBS])
    for data in dataset[OBS]:
        obs: Dict[str, Any] = {}
        obs = {
            **obs,
            **__get_element_to_list(data, mode=OBSKEY),
            OBSVALUE.upper(): data[OBSVALUE][VALUE.lower()],
        }
        if ATTRIBUTES in data:
            obs = {**obs, **__get_element_to_list(data, mode=ATTRIBUTES)}
        test_list.append({**obs})
        test_list, df = __process_df(test_list, df)

    test_list, df = __process_df(test_list, df, is_end=True)

    return df


def __get_at_att_gen(dataset: Dict[str, Any]) -> Dict[str, Any]:
    """Gets all the elements if it is Generic data."""
    attached_attributes: Dict[str, Any] = {}
    if ATTRIBUTES not in dataset:
        return attached_attributes
    dataset[ATTRIBUTES][VALUE] = add_list(dataset[ATTRIBUTES][VALUE])
    for k in dataset[ATTRIBUTES][VALUE]:
        attached_attributes[k[ID]] = k[VALUE.lower()]
    return attached_attributes


def __parse_generic_data(
    dataset: Dict[str, Any], structure_info: Dict[str, Any]
) -> PandasDataset:
    attached_attributes = __get_at_att_gen(dataset)

    # Parsing data
    if SERIES in dataset:
        # Generic Series
        df = __reading_generic_series(dataset)
    else:
        # Generic All Dimensions
        df = __reading_generic_all(dataset)

    urn = f"{structure_info['structure_type']}={structure_info['unique_id']}"

    return PandasDataset(
        structure=urn, attributes=attached_attributes, data=df
    )


def read(input_str: str, validate: bool = True) -> Sequence[PandasDataset]:
    """Reads an SDMX-ML 2.1 Generic data and returns a Sequence of Datasets.

    Args:
        input_str: SDMX-ML data to read.
        validate: If True, the XML data will be validated against the XSD.
    """
    dict_info = parse_xml(input_str, validate=validate)
    if GENERIC not in dict_info:
        raise Invalid("This SDMX document is not SDMX-ML 2.1 Generic.")
    dataset_info, str_info = get_data_objects(dict_info[GENERIC])

    datasets = []
    for dataset in dataset_info:
        ds = __parse_generic_data(dataset, str_info[dataset[STRREF]])
        datasets.append(ds)
    return datasets
