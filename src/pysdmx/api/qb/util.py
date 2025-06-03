"""Utility classes for pysdmx REST query builders."""

import re
from abc import abstractmethod
from enum import IntEnum
from typing import Any, Sequence, Union

import msgspec

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
    V2_2_0 = 10
    V2_2_1 = 11


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


class CoreQuery(msgspec.Struct, frozen=True, omit_defaults=True):
    def get_url(self, version: ApiVersion, omit_defaults: bool = False) -> str:
        """The URL for the query in the selected SDMX-REST API version."""
        self._validate_query(version)
        if omit_defaults:
            return self._create_short_query(version)
        else:
            return self._create_full_query(version)

    def validate(self) -> None:
        """Validate the query."""
        try:
            self._get_decoder().decode(_encoder.encode(self))
        except msgspec.DecodeError as err:
            raise Invalid("Invalid Schema Query", str(err)) from err

    def _to_kw(self, val: str, ver: ApiVersion) -> str:
        if val == "*" and ver < ApiVersion.V2_0_0:
            val = "all"
        elif val == "~" and ver < ApiVersion.V2_0_0:
            val = "latest"
        return val

    def _to_kws(self, vals: Union[str, Sequence[str]], ver: ApiVersion) -> str:
        vals = [vals] if isinstance(vals, str) else vals
        mapped = [self._to_kw(v, ver) for v in vals]
        return ",".join(mapped)

    def _join_mult(self, vals: Union[str, Sequence[str]]) -> str:
        return vals if isinstance(vals, str) else ",".join(vals)

    def _append_qs_param(
        self, qs: str, value: Any, field: str, disp_value: Any = None
    ) -> str:
        if value or (not isinstance(value, bool) and value == 0):
            if qs:
                qs += "&"
            qs += f"{field}={disp_value if disp_value else value}"
        return qs

    @abstractmethod
    def _get_decoder(self) -> msgspec.json.Decoder:  # type: ignore[type-arg]
        """Returns the decoder to be used for validation."""

    @abstractmethod
    def _validate_query(self, version: ApiVersion) -> None:
        """Any additional validation steps to be performed by subclasses."""

    @abstractmethod
    def _create_full_query(self, ver: ApiVersion) -> str:
        """Creates a URL, with default values."""

    @abstractmethod
    def _create_short_query(self, ver: ApiVersion) -> str:
        """Creates a URL, omitting default values when possible."""


_encoder = msgspec.json.Encoder()

__all__ = ["ApiVersion", "check_multiple_items", "check_multiple_data_context"]
