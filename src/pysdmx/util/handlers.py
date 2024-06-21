"""
    Handlers file provide functions to make the code more readable
"""
import pandas as pd


def first_element_dict(obj_: dict):
    if len(obj_) != 0:
        values_view = obj_.values()
        value_iterator = iter(values_view)
        first_value = next(value_iterator)
        return first_value
    else:
        return None


def split_unique_id(obj_: str):
    data = obj_.split(':', 1)
    agencyID = data[0]
    data = data[1].split('(', 1)
    id = data[0]
    version = data[1].split(')', 1)[0]

    return agencyID, id, version


def split_from_urn(obj_: str, split_id=True):
    full_id = obj_.split("=", 1)[1]
    if split_id:
        return split_unique_id(full_id)
    return full_id


def add_list(element: any):
    if not isinstance(element, list):
        element = [element]
    return element


def unique_id(agencyID, id_, version):
    return f"{agencyID}:{id_}({version})"


def drop_na_all(df: pd.DataFrame):
    return df.dropna(axis=1, how="all")
