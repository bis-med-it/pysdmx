"""API for FMR readers."""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


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
