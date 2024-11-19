"""Collection of utility functions."""

import re
from typing import Any, Sequence

from msgspec import Struct

from pysdmx.errors import Invalid, NotFound
from pysdmx.model import Agency
from pysdmx.util._date_pattern_map import convert_dpm

NF = "Not found"


class Reference(Struct, frozen=True):
    """The coordinates of an SDMX maintainable artefact.

    Attributes:
        sdmx_type: The type of SDMX artefact (``codelist``, etc.)
        agency: The maintainer of the artefact (e.g. ``BIS``, ``SDMX``, etc.)
        id: The artefact ID (e.g. ``CL_FREQ``)
        version: The artefact version (e.g. ``1.0.0``)
    """

    sdmx_type: str
    agency: str
    id: str
    version: str

    def __str__(self) -> str:
        """Returns a string representation of the object."""
        return f"{self.sdmx_type}={self.agency}:{self.id}({self.version})"


class ItemReference(Struct, frozen=True):
    """The coordinates of an SDMX non-nested item.

    Attributes:
        sdmx_type: The type of SDMX artefact (``concept``, etc.)
        agency: The maintainer of the artefact (e.g. ``BIS``, etc.)
        id: The maintainable ID (e.g. ``CL_FREQ``)
        version: The artefact version (e.g. ``1.0.0``)
        item_id: The item ID (e.g. ``A``)
    """

    sdmx_type: str
    agency: str
    id: str
    version: str
    item_id: str


maintainable_urn_pattern = re.compile(r"^.*\.(.*)=(.*):(.*)\((.*)\)$")
item_urn_pattern = re.compile(r"^.*\.(.*)=(.*):(.*)\((.*)\)\.(.*)$")


def parse_urn(urn: str) -> Reference:
    """Parses an SDMX urn and returns an object with the details."""
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
    """Parses an SDMX item urn and returns an object with the details."""
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


__all__ = ["convert_dpm", "find_by_urn", "parse_item_urn", "parse_urn"]
