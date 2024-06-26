"""Module that holds the necessary functions to read xml files."""

import itertools
from typing import Any, Dict

import numpy as np
import pandas as pd

from pysdmx.io.xml.sdmx21.__parsing_config import (
    AGENCY_ID,
    ATTRIBUTES,
    DIM_OBS,
    exc_attributes,
    GENERIC,
    GROUP,
    ID,
    OBS,
    OBS_DIM,
    OBSKEY,
    OBSVALUE,
    REF,
    SERIES,
    SERIESKEY,
    STR_USAGE,
    STRID,
    STRREF,
    STRSPE,
    STRUCTURE,
    URN,
    VALUE,
    VERSION,
)
from pysdmx.util.handlers import add_list, split_from_urn

chunksize = 50000


class Dataset:
    """Class containing the necessary attributes to create the Dataset.

    Args:
            attached_attributes: Attached attributes from the xml file.
            data: Dataframe.
            structure_type: Generic or Specific.
            unique_id: DimensionAtObservation.
    """

    __slots__ = ("attached_attributes", "data", "unique_id", "structure_type")

    def __init__(self, attached_attributes, data, unique_id, structure_type):
        """Attributes."""
        self.attached_attributes = attached_attributes
        self.data = data
        self.unique_id = unique_id
        self.structure_type = structure_type


def __get_element_to_list(data, mode):
    obs = {}
    if VALUE in data[mode]:
        data[mode][VALUE] = add_list(data[mode][VALUE])
        for k in data[mode][VALUE]:
            obs[k[ID]] = k[VALUE.lower()]
    return obs


def __process_df(test_list: list, df: pd.DataFrame):
    if len(test_list) > 0:
        if df is not None:
            df = pd.concat([df, pd.DataFrame(test_list)], ignore_index=True)
        else:
            df = pd.DataFrame(test_list)

    del test_list[:]

    return test_list, df


def __reading_generic_series(dataset) -> pd.DataFrame:
    # Generic Series
    test_list = []
    df = None
    dataset[SERIES] = add_list(dataset[SERIES])
    for series in dataset[SERIES]:
        keys = {}
        # Series Keys
        if not isinstance(series[SERIESKEY][VALUE], list):
            series[SERIESKEY][VALUE] = [series[SERIESKEY][VALUE]]
        for v in series[SERIESKEY][VALUE]:
            keys[v[ID]] = v[VALUE.lower()]
        if ATTRIBUTES in series:
            if not isinstance(series[ATTRIBUTES][VALUE], list):
                series[ATTRIBUTES][VALUE] = [series[ATTRIBUTES][VALUE]]
            for v in series[ATTRIBUTES][VALUE]:
                keys[v[ID]] = v[VALUE.lower()]
        if not isinstance(series[OBS], list):
            series[OBS] = [series[OBS]]
        for data in series[OBS]:
            obs = {OBS_DIM: data[OBS_DIM][VALUE.lower()]}
            if OBSVALUE in data:
                obs[OBSVALUE.upper()] = data[OBSVALUE][VALUE.lower()]
            else:
                obs[OBSVALUE.upper()] = None
            if ATTRIBUTES in data:
                obs = {**obs, **__get_element_to_list(data, mode=ATTRIBUTES)}
            test_list.append({**keys, **obs})
        if len(test_list) > chunksize:
            test_list, df = __process_df(test_list, df)

    test_list, df = __process_df(test_list, df)

    return df


def __reading_generic_all(dataset) -> pd.DataFrame:
    # Generic All Dimensions
    test_list = []
    df = None
    dataset[OBS] = add_list(dataset[OBS])
    for data in dataset[OBS]:
        obs = {}
        obs = {**obs, **__get_element_to_list(data, mode=OBSKEY)}
        if ID in data[OBSVALUE]:
            obs[data[OBSVALUE][ID]] = data[OBSVALUE][VALUE.lower()]
        else:
            obs[OBSVALUE.upper()] = data[OBSVALUE][VALUE.lower()]
        if ATTRIBUTES in data:
            obs = {**obs, **__get_element_to_list(data, mode=ATTRIBUTES)}
        test_list.append({**obs})
        if len(test_list) > chunksize:
            test_list, df = __process_df(test_list, df)

    test_list, df = __process_df(test_list, df)

    return df


def __reading_str_series(dataset) -> pd.DataFrame:
    # Structure Specific Series
    test_list = []
    df = None
    dataset[SERIES] = add_list(dataset[SERIES])
    for data in dataset[SERIES]:
        keys = dict(itertools.islice(data.items(), len(data) - 1))
        if not isinstance(data[OBS], list):
            data[OBS] = [data[OBS]]
        for j in data[OBS]:
            test_list.append({**keys, **j})
        if len(test_list) > chunksize:
            test_list, df = __process_df(test_list, df)

    test_list, df = __process_df(test_list, df)

    return df


def __reading_group_data(dataset) -> pd.DataFrame:
    # Structure Specific Group Data
    test_list = []
    df = None
    dataset[GROUP] = add_list(dataset[GROUP])
    for data in dataset[GROUP]:
        test_list.append(dict(data.items()))
        if len(test_list) > chunksize:
            test_list, df = __process_df(test_list, df)
    test_list, df = __process_df(test_list, df)

    cols_to_delete = [x for x in df.columns if ":type" in x]
    for x in cols_to_delete:
        del df[x]

    df = df.drop_duplicates(keep="first").reset_index(drop=True)

    return df


def __get_at_att_str(dataset):
    """Gets the elements of the dataset if it is Structure Specific Data."""
    return {k: dataset[k] for k in dataset if k not in exc_attributes}


def __get_at_att_gen(dataset):
    """Gets all the elements if it is Generic data."""
    attached_attributes = {}
    if VALUE in dataset[ATTRIBUTES]:
        dataset[ATTRIBUTES][VALUE] = add_list(dataset[ATTRIBUTES][VALUE])
        for k in dataset[ATTRIBUTES][VALUE]:
            attached_attributes[k[ID]] = k[VALUE.lower()]
    return attached_attributes


def __get_ids_from_structure(element: Dict[str, Any]):
    """Gets the agency_id, id and version of the structure.

    Args:
        element: The data hold in the structure.

    Raises:
        Exception: If structure reference cannot be extracted.

    Returns:
        If the element is REF, agency_id, id and version may be returned.
        If the element is URN, agency_id, id and version would be taken from
        split function.
    """
    if REF in element:
        agency_id = element[REF][AGENCY_ID]
        id_ = element[REF][ID]
        version = element[REF][VERSION]
        return agency_id, id_, version
    elif URN in element:
        return split_from_urn(element[URN])
    raise Exception("Can not extract structure reference")


def __get_elements_from_structure(structure):
    """Gets elements according to the xml type of file.

    Args:
        structure: It can appear in two ways:
            If structure is 'STRUCTURE', it will get
            the ids related to STRUCTURE.
            If structure is 'STR_USAGE', it will get
            the ids related to STR_USAGE.

    Returns:
        The ids contained in the structure will be returned.
    """
    if STRUCTURE in structure:
        structure_type = "datastructure"
        tuple_ids = __get_ids_from_structure(structure[STRUCTURE])

    elif STR_USAGE in structure:
        structure_type = "dataflow"
        tuple_ids = __get_ids_from_structure(structure[STR_USAGE])
    else:
        return None, None, None, None
    return tuple_ids + (structure_type,)


def __extract_structure(structure):
    """Extracts elements contained in the structure."""
    structure = add_list(structure)
    str_info = {}
    for str_item in structure:
        (agency_id, id_, version, structure_type) = (
            __get_elements_from_structure(str_item)
        )
        if agency_id is not None:
            str_id = f"{agency_id}:{id_}({version})"
        else:
            str_id = f"{id_}({version})"
        str_info[str_item[STRID]] = {
            DIM_OBS: str_item[DIM_OBS],
            "unique_id": str_id,
            "structure_type": structure_type,
        }

    return str_info


def create_dataset(dataset, str_info, global_mode):
    """Takes the information contained in the xml files to fulfill the dataset and return a pandas dataframe.

    Args:
        dataset: The dataset created.
        str_info: Dict that contains info
            such as agency_id, id and its version.
        global_mode: Identifies if the xml file has
            Generic data or a StructureSpecificData.

    Returns:
        A pandas dataframe with the created dataset will be returned.

    Raises:
        Exception: If the structure reference cannot be found.
    """
    if dataset[STRREF] not in str_info:
        raise Exception(
            f"Cannot find the structure reference "
            f"of this dataset:{dataset[STRREF]}"
        )
    value = str_info[dataset[STRREF]]
    if STRSPE == global_mode:
        # Dataset info
        attached_attributes = __get_at_att_str(dataset)

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
        else:
            df = pd.DataFrame()
    elif GENERIC == global_mode:

        # Dataset info
        if ATTRIBUTES in dataset:
            attached_attributes = __get_at_att_gen(dataset)
        else:
            attached_attributes = {}

        # Parsing data
        if SERIES in dataset:
            # Generic Series
            df = __reading_generic_series(dataset)
            renames = {"OBSVALUE": "OBS_VALUE", "ObsDimension": value[DIM_OBS]}
            df.rename(columns=renames, inplace=True)
        elif OBS in dataset:
            # Generic All Dimensions
            df = __reading_generic_all(dataset)
            df.replace(np.nan, "", inplace=True)
            df.rename(columns={"OBSVALUE": "OBS_VALUE"}, inplace=True)
        else:
            df = pd.DataFrame()
    else:
        raise Exception
    dataset = Dataset(
        attached_attributes=attached_attributes,
        data=df,
        unique_id=value["unique_id"],
        structure_type=value["structure_type"],
    )

    return dataset
