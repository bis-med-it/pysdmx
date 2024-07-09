"""Utility functions for XML parsing and serialization."""

from typing import Any, List


def add_list(element: Any) -> List[Any]:
    """Make sure an element is a list and convert it if it is not.

    The xmltodict library always returns a list if there are multiple elements
    but a dict if there is only one element. This function makes sure that the
    element is always a list.

    Args:
        element: The element to be converted

    Returns:
        A list with the element
    """
    if not isinstance(element, list):
        element = [element]
    return element
