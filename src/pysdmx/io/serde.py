"""Serializers and deserializers for SDMX messages."""

from dataclasses import dataclass
from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class Deserializer(Protocol):
    """Parses a message and return domain objects."""

    def to_model(self) -> Any:
        """Returns the domain objects."""


@runtime_checkable
class Serializer(Protocol):
    """Creates an SDMX message from domain objects."""

    @classmethod
    def from_model(self, message: Any) -> Any:
        """Returns the SDMX message."""


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
    metadataflows: Deserializer
    metadata_provision_agreement: Deserializer
    metadata_providers: Deserializer
    msds: Deserializer


@dataclass
class Serializers:
    """Collection of serializers for a format."""

    structure_message: Serializer
    metadata_message: Serializer


@dataclass
class GdsDeserializers:
    """Collection of GDS deserializers for a format."""

    agencies: Any
    catalogs: Any
    sdmx_api: Any
    services: Any
    urn_resolver: Any
