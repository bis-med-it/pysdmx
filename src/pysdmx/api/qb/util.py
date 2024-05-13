from enum import Enum
import re

from pysdmx.errors import ClientError


class _ApiVersion:
    def __init__(self, label: str, number: int) -> None:
        self.label = label
        self.number = number

    def __str__(self) -> str:
        return self.label

    def __hash__(self) -> int:
        return hash(self.label)


class ApiVersion(Enum):
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
        return self.value.number < other.value.number

    def __lte__(self, other: "ApiVersion") -> bool:
        return self.value.number <= other.value.number

    def __gt__(self, other: "ApiVersion") -> bool:
        return self.value.number > other.value.number

    def __gte__(self, other: "ApiVersion") -> bool:
        return self.value.number >= other.value.number


MULT_SEP = re.compile(r"\+")


def check_multiple_items(value: str, version: ApiVersion) -> None:
    if version < ApiVersion.V1_3_0 and re.search(MULT_SEP, value):
        raise ClientError(
            422,
            "Validation Error",
            f"Multiple items not allowed in SDMX-REST {version.value.label}.",
        )
