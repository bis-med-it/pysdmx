"""Handlers file provide functions to make the code more readable."""

# import pandas as pd


def first_element_dict(obj_: dict):
    """First element dict.

    Args:
        obj_: An object

    Returns:
        dict: A dict with the first element.
    """
    if len(obj_) != 0:
        values_view = obj_.values()
        value_iterator = iter(values_view)
        first_value = next(value_iterator)
        return first_value
    else:
        return None


def split_unique_id(obj_: str):
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


def split_from_urn(obj_: str, split_id=True):
    """Split from urn.

    Args:
        obj_: String with the name of the object.
        split_id: True splits the id.

    Returns:
        full id may be returned.
    """
    full_id = obj_.split("=", 1)[1]
    if split_id:
        return split_unique_id(full_id)
    return full_id


def add_list(element: any):
    """Adds data contained in the xml Dataset into a list if it is possible.

    Args:
        element: The elements contained in the Dataset.

    Returns:
        The elements in a list.
    """
    if not isinstance(element, list):
        element = [element]
    return element


def unique_id(agencyID, id_, version):
    """Unique_id.

    Args:
        agencyID: Name of the agency.
        id_: The id.
        version: Version.

    Returns:
        A string with the info contained in the reference.
    """
    return f"{agencyID}:{id_}({version})"


# def drop_na_all(df: pd.DataFrame):
#     """
#
#     """
#     return df.dropna(axis=1, how="all")
