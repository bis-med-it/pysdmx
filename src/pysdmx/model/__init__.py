"""SDMX simplified **domain model**, expressed as **Python classes**.

This module contains data classes representing a **simplified and opinionated
subset** of the SDMX information model.
"""

from re import Pattern
from typing import Any

from pysdmx.model.category import Category, CategoryScheme
from pysdmx.model.code import Code, Codelist, HierarchicalCode, Hierarchy
from pysdmx.model.concept import Concept, ConceptScheme, DataType, Facets
from pysdmx.model.dataflow import (
    ArrayBoundaries,
    Component,
    Components,
    DataflowInfo,
    Role,
    Schema,
)
from pysdmx.model.map import (
    ComponentMap,
    DatePatternMap,
    ImplicitComponentMap,
    MappingDefinition,
    MultiComponentMap,
    MultiValueMap,
    ValueMap,
    FixedValueMap,
)
from pysdmx.model.metadata import MetadataAttribute, MetadataReport
from pysdmx.model.organisation import Contact, DataflowRef, Organisation


def encoders(obj: Any) -> Any:
    """Encoders for msgspec serialization.

    The pysdmx model classes are based on msgspec `Struct` classes. These
    classes offer serialization and deserialization into various formats
    for many Python types. However, some types used in pysdmx are not
    supported. This will lead to serialization errors, unless `encoders`
    is used. See details at https://jcristharif.com/msgspec/extending.html.

    For example:

        import msgspec
        from pysdmx.model import encoders
        encoder = msgspec.json.Encoder(enc_hook=encoders)

    Args:
        obj: The object to be encoded

    Returns:
        The received object converted to supported Python types

    Raises:
        NotImplementedError: In case the object type is not one of the types
            needing conversion
    """
    if isinstance(obj, Pattern):
        return f"regex:{obj.pattern}"
    elif isinstance(obj, Components):
        return list(obj)
    else:
        # Raise a NotImplementedError for other types
        raise NotImplementedError(
            f"Objects of type {type(obj)} are not supported"
        )


__all__ = [
    "ArrayBoundaries",
    "Category",
    "CategoryScheme",
    "Code",
    "Codelist",
    "Component",
    "Components",
    "ComponentMap",
    "Concept",
    "ConceptScheme",
    "Contact",
    "DataflowInfo",
    "DataflowRef",
    "DataType",
    "DatePatternMap",
    "Facets",
    "HierarchicalCode",
    "Hierarchy",
    "ImplicitComponentMap",
    "MappingDefinition",
    "MetadataAttribute",
    "MetadataReport",
    "MultiComponentMap",
    "MultiValueMap",
    "Organisation",
    "Role",
    "Schema",
    "ValueMap",
    "FixedValueMap",
]
