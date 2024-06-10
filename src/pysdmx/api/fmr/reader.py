"""API for FMR readers."""

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Dict, List, Protocol, runtime_checkable, Sequence

from pysdmx.model import MetadataAttribute


@runtime_checkable
class Deserializer(Protocol):
    """Parses a message and return domain objects."""

    def to_model(self) -> Any:
        """Returns the domain objects."""


@dataclass
class Deserializers:
    """Collection of deserializers for a format."""

    agencies: Deserializer
    categories: Deserializer
    codes: Deserializer
    concepts: Deserializer
    dataflow: Deserializer
    providers: Deserializer
    schema: Deserializer
    hier_assoc: Deserializer
    hierarchy: Deserializer
    report: Deserializer
    mapping: Deserializer
    code_map: Deserializer


def _merge_attributes(
    attrs: Sequence[MetadataAttribute],
) -> Sequence[MetadataAttribute]:
    """Groups together the values of attributes with the same ID.

    The function assumes that an attribute will either have a
    value or will act as a container for other attributes. In
    case the attribute contains other attributes AND has a value,
    this function will NOT work as expected.

    Args:
        attrs: The list of attributes to be merged

    Returns:
        The list of (possibly merged) attributes
    """
    by_id: Dict[str, List[Any]] = defaultdict(list)
    sub_id = []

    for attr in attrs:
        if attr.attributes:
            sub_id.append(
                MetadataAttribute(
                    attr.id,
                    attr.value,
                    _merge_attributes(attr.attributes),
                )
            )
        else:
            by_id[attr.id].append(attr.value)

    out = []
    out.extend(sub_id)
    for k, v in by_id.items():
        val = v if len(v) > 1 else v[0]
        out.append(MetadataAttribute(k, val))
    return out
