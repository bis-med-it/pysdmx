"""Serializers and deserializers for SDMX messages."""

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
    categorisation: Deserializer
    codes: Deserializer
    concepts: Deserializer
    dataflow_info: Deserializer
    dataflows: Deserializer
    providers: Deserializer
    provision_agreement: Deserializer
    schema: Deserializer
    hier_assoc: Deserializer
    hierarchy: Deserializer
    report: Deserializer
    mapping: Deserializer
    code_map: Deserializer
    transformation_scheme: Deserializer


@dataclass
class GdsDeserializers:
    """Collection of GDS deserializers for a format."""

    agencies: Any
    catalogs: Any
    sdmx_api: Any
    services: Any
    urn_resolver: Any
