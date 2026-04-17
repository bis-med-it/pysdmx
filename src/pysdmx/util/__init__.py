"""Collection of utility functions."""

import re
from typing import Any, Sequence, Union

from pysdmx.errors import Invalid, NotFound
from pysdmx.model import Agency, ItemReference, Reference
from pysdmx.util._date_pattern_map import convert_dpm
from pysdmx.util._net_utils import map_httpx_errors

NF = "Not found"

maintainable_urn_pattern = re.compile(r"^.*\.(.*)=(.*):(.*)\((.*)\)$")
item_urn_pattern = re.compile(r"^.*\.(.*)=(.*):(.*)\((.*)\)\.(.*)$")
short_urn_pattern = re.compile(r"^(.*)=(.*):(.*)\((.*)\)$")
short_item_urn_pattern = re.compile(r"^(.*)=(.*):(.*)\((.*)\)\.(.*)$")
_SEMVER_NUM = r"(0|[1-9]\d*)"
semver_final_pattern = re.compile(rf"^[1-9]\d*\.{_SEMVER_NUM}\.{_SEMVER_NUM}$")


def parse_urn(urn: str) -> Union[ItemReference, Reference]:
    """Parses an SDMX urn and returns the details."""
    try:
        return parse_maintainable_urn(urn)
    except Invalid:
        try:
            return parse_item_urn(urn)
        except Invalid:
            try:
                return parse_short_urn(urn)
            except Invalid:
                try:
                    return parse_short_item_urn(urn)
                except Invalid:
                    raise Invalid(
                        NF, "{urn} does not match any known pattern"
                    ) from None


def parse_maintainable_urn(urn: str) -> Reference:
    """Parses an SDMX maintainable urn and returns the details."""
    m = re.match(maintainable_urn_pattern, urn)
    if m:
        return Reference(
            sdmx_type=m.group(1),
            agency=m.group(2),
            id=m.group(3),
            version=m.group(4),
        )
    else:
        raise Invalid(NF, f"{urn} does not match {maintainable_urn_pattern}")


def parse_item_urn(urn: str) -> ItemReference:
    """Parses an SDMX item urn and returns the details."""
    m = re.match(item_urn_pattern, urn)
    if m:
        return ItemReference(
            sdmx_type=m.group(1),
            agency=m.group(2),
            id=m.group(3),
            version=m.group(4),
            item_id=m.group(5),
        )
    else:
        raise Invalid(NF, f"{urn} does not match {item_urn_pattern}.")


def parse_short_urn(urn: str) -> Reference:
    """Parses an SDMX short urn and returns the details."""
    m = re.match(short_urn_pattern, urn)
    if m:
        return Reference(
            sdmx_type=m.group(1),
            agency=m.group(2),
            id=m.group(3),
            version=m.group(4),
        )
    else:
        raise Invalid(NF, f"{urn} does not match {short_urn_pattern}.")


def parse_short_item_urn(urn: str) -> ItemReference:
    """Parses an SDMX short item urn and returns the details."""
    m = re.match(short_item_urn_pattern, urn)
    if m:
        return ItemReference(
            sdmx_type=m.group(1),
            agency=m.group(2),
            id=m.group(3),
            version=m.group(4),
            item_id=m.group(5),
        )
    else:
        raise Invalid(NF, f"{urn} does not match {short_item_urn_pattern}.")


def is_final(version: str) -> bool:
    """Infers finality from an SDMX 3.0 semantic version string.

    In SDMX 3.0+, the isFinal attribute no longer exists. Instead,
    a version with three numeric segments and no hyphen extension
    (e.g. 1.0.0) is considered final, while versions with a hyphen
    extension (e.g. 1.0.0-draft) or only two segments (e.g. 1.0)
    are not final.

    Args:
        version: The version string to evaluate.

    Returns:
        True if the version indicates a final artefact.
    """
    return bool(semver_final_pattern.match(version))


def find_by_urn(artefacts: Sequence[Any], urn: str) -> Any:
    """Returns the maintainable artefact matching the supplied urn."""
    r = parse_urn(urn)
    f = [
        a
        for a in artefacts
        if (
            (
                a.agency == r.agency
                or (
                    a.agency.id == r.agency
                    if isinstance(a.agency, Agency)
                    else False
                )
            )
            and a.id == r.id
            and a.version == r.version
        )
    ]
    if f:
        return f[0]
    else:
        urns = [f"{a.agency}:{a.id}({a.version})" for a in artefacts]
        raise NotFound(
            NF,
            (
                f"Could not find an artefact matching the following URN: "
                f"{urn}. The artefacts received were: {urns}."
            ),
        )


def experimental(cls: type) -> type:
    """Decorator to mark a class as experimental."""
    if isinstance(cls, type):
        t = (
            "Warning: This class is experimental and subject to change \n"
            "without prior notice. It is not covered by semantic versioning \n"
            "guarantees, and modifications to this class will not result in \n"
            "a major version increment. Use it with caution in production \n"
            "environments or critical processes."
        )
        cls.__doc__ = f"{cls.__doc__}\n\n{t}" if cls.__doc__ else t

    return cls


__all__ = [
    "convert_dpm",
    "experimental",
    "find_by_urn",
    "is_final",
    "parse_item_urn",
    "parse_maintainable_urn",
    "parse_urn",
    "parse_short_urn",
    "parse_short_item_urn",
    "ItemReference",
    "Reference",
    "map_httpx_errors",
]
