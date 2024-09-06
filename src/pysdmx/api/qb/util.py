"""Utility classes for pysdmx REST query builders."""

from enum import IntEnum
import re
from typing import Sequence, Union

from pysdmx.errors import Invalid


class ApiVersion(IntEnum):
    """The version of the SDMX-REST API."""

    V1_0_0 = 0
    V1_0_1 = 1
    V1_0_2 = 2
    V1_1_0 = 3
    V1_2_0 = 4
    V1_3_0 = 5
    V1_4_0 = 6
    V1_5_0 = 7
    V2_0_0 = 8
    V2_1_0 = 9


MULT_SEP = re.compile(r"\+")
REST_ALL = "*"
REST_LATEST = "~"


def check_multiple_items(
    value: Union[str, Sequence[str]], version: ApiVersion
) -> None:
    """Whether multiple items are supported in the supplied API version."""
    if not isinstance(value, str) and version < ApiVersion.V1_3_0:
        raise Invalid(
            "Validation Error",
            f"Multiple items not allowed in SDMX-REST {version.value}.",
        )


def check_multiple_data_context(
    field: str, value: Union[str, Sequence[str]], version: ApiVersion
) -> None:
    """Whether multiple items are supported in the supplied API version."""
    if not isinstance(value, str) and version < ApiVersion.V2_0_0:
        raise Invalid(
            "Validation Error",
            (
                f"More than one {field} is not allowed in data context "
                f"for SDMX-REST {version.value}."
            ),
        )


__all__ = ["ApiVersion", "check_multiple_items", "check_multiple_data_context"]
