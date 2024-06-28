"""Handlers file provide functions to make the code more readable."""

from typing import Any


# import pandas as pd


def split_unique_id(obj_: str) -> tuple[str, str, str]:
    """Split unique id.

    Args:
        obj_: String with the name of the object.

    Returns:
        agencyID, id and version.
    """
    data = obj_.split(":", 1)
    agencyID = data[0]
    data = data[1].split("(", 1)
    id = data[0]
    version = data[1].split(")", 1)[0]

    return agencyID, id, version


def split_from_urn(obj_: str, split_id: bool = True) -> Any:
    """Split from urn.

    Args:
        obj_: String with the name of the object.
        split_id: True splits the id.

    Returns:
        full id.
    """
    full_id = obj_.split("=", 1)[1]
    if split_id:
        return split_unique_id(full_id)
    return full_id


def add_list(element: Any) -> Any:
    """Adds data contained in the xml Dataset into a list if it is possible.

    Args:
        element: The elements contained in the Dataset.

    Returns:
        The elements in a list.
    """
    if not isinstance(element, list):
        element = [element]
    return element


def unique_id(agency_id: str, id_: str, version: str) -> str:
    """Unique_id.

    Args:
        agency_id: Name of the agency.
        id_: The id.
        version: Version.

    Returns:
        A string with the info contained in the reference.
    """
    return f"{agency_id}:{id_}({version})"


# def drop_na_all(df: pd.DataFrame):
#     """
#
#     """
#     return df.dropna(axis=1, how="all")
