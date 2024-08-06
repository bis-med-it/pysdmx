"""Utility classes for pysdmx REST query builders."""

from enum import Enum
import re
from typing import Sequence, Union

from pysdmx.errors import ClientError


class _ApiVersion:
    def __init__(self, label: str, number: int) -> None:
        self.label = label
        self.number = number

    def __str__(self) -> str:
        return self.label

    def __hash__(self) -> int:
        return hash(self.label)

    def __lt__(self, other: "_ApiVersion") -> bool:
        """Whether this version is less than the supplied one."""
        return self.number < other.number

    def __le__(self, other: "_ApiVersion") -> bool:
        """Whether this version is less or equal to the supplied one."""
        return self.number <= other.number

    def __gt__(self, other: "_ApiVersion") -> bool:
        """Whether this version is greater than the supplied one."""
        return self.number > other.number

    def __ge__(self, other: "_ApiVersion") -> bool:
        """Whether this version is greater or equal to the supplied one."""
        return self.number >= other.number


_V1_0_0 = _ApiVersion("V1.0.0", 0)
_V1_0_1 = _ApiVersion("V1.0.1", 1)
_V1_0_2 = _ApiVersion("V1.0.2", 2)
_V1_1_0 = _ApiVersion("V1.1.0", 3)
_V1_2_0 = _ApiVersion("V1.2.0", 4)
_V1_3_0 = _ApiVersion("V1.3.0", 5)
_V1_4_0 = _ApiVersion("V1.4.0", 6)
_V1_5_0 = _ApiVersion("V1.5.0", 7)
_V2_0_0 = _ApiVersion("V2.0.0", 8)
_V2_1_0 = _ApiVersion("V2.1.0", 9)


class ApiVersion(Enum):
    """The version of the SDMX-REST API."""

    V1_0_0 = _V1_0_0
    V1_0_1 = _V1_0_1
    V1_0_2 = _V1_0_2
    V1_1_0 = _V1_1_0
    V1_2_0 = _V1_2_0
    V1_3_0 = _V1_3_0
    V1_4_0 = _V1_4_0
    V1_5_0 = _V1_5_0
    V2_0_0 = _V2_0_0
    V2_1_0 = _V2_1_0

    def __lt__(self, other: "ApiVersion") -> bool:
        """Whether this version is less than the supplied one."""
        return self.value < other.value

    def __le__(self, other: "ApiVersion") -> bool:
        """Whether this version is less or equal to the supplied one."""
        return self.value <= other.value

    def __gt__(self, other: "ApiVersion") -> bool:
        """Whether this version is greater than the supplied one."""
        return self.value > other.value

    def __ge__(self, other: "ApiVersion") -> bool:
        """Whether this version is greater or equal to the supplied one."""
        return self.value >= other.value


MULT_SEP = re.compile(r"\+")
REST_ALL = "*"
REST_LATEST = "~"


def check_multiple_items(
    value: Union[str, Sequence[str]], version: ApiVersion
) -> None:
    """Whether multiple items are supported in the supplied API version."""
    if not isinstance(value, str) and version < ApiVersion.V1_3_0:
        raise ClientError(
            422,
            "Validation Error",
            f"Multiple items not allowed in SDMX-REST {version.value.label}.",
        )


def check_multiple_data_context(
    field: str, value: Union[str, Sequence[str]], version: ApiVersion
) -> None:
    """Whether multiple items are supported in the supplied API version."""
    if not isinstance(value, str) and version < ApiVersion.V2_0_0:
        raise ClientError(
            422,
            "Validation Error",
            (
                f"More than one {field} is not allowed in data context "
                f"for SDMX-REST {version.value.label}."
            ),
        )


__all__ = ["ApiVersion"]
