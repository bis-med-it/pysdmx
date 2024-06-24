"""Utility classes for pysdmx REST query builders."""

from enum import Enum
import re
from typing import Sequence, Union

from msgspec import Struct

from pysdmx.errors import ClientError


class _ApiVersion(Struct, frozen=True):
    label: str
    number: int

    def __str__(self) -> str:
        return self.label

    def __hash__(self) -> int:
        return hash(self.label)


class ApiVersion(Enum):
    """The version of the SDMX-REST API."""

    V1_0_0 = _ApiVersion("V1.0.0", 0)
    V1_0_1 = _ApiVersion("V1.0.1", 1)
    V1_0_2 = _ApiVersion("V1.0.2", 2)
    V1_1_0 = _ApiVersion("V1.1.0", 3)
    V1_2_0 = _ApiVersion("V1.2.0", 4)
    V1_3_0 = _ApiVersion("V1.3.0", 5)
    V1_4_0 = _ApiVersion("V1.4.0", 6)
    V1_5_0 = _ApiVersion("V1.5.0", 7)
    V2_0_0 = _ApiVersion("V2.0.0", 8)
    V2_1_0 = _ApiVersion("V2.1.0", 9)

    def __lt__(self, other: "ApiVersion") -> bool:
        """Whether this version is less than the supplied one."""
        return self.value.number < other.value.number

    def __lte__(self, other: "ApiVersion") -> bool:
        """Whether this version is less or equal to the supplied one."""
        return self.value.number <= other.value.number

    def __gt__(self, other: "ApiVersion") -> bool:
        """Whether this version is greater than the supplied one."""
        return self.value.number > other.value.number

    def __gte__(self, other: "ApiVersion") -> bool:
        """Whether this version is greater or equal to the supplied one."""
        return self.value.number >= other.value.number


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


__all__ = ["ApiVersion"]
