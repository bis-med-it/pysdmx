"""SDMX simplified **domain model**, expressed as **Python classes**.

This module contains data classes representing a **simplified and opinionated
subset** of the SDMX information model.
"""

from typing import Any, Type

import msgspec

from pysdmx.errors import NotImplemented
from pysdmx.model.__base import (
    Agency,
    Contact,
    DataConsumer,
    DataflowRef,
    DataProvider,
    MetadataProvider,
    Organisation,
)
from pysdmx.model.category import Category, CategoryScheme
from pysdmx.model.code import (
    Code,
    Codelist,
    HierarchicalCode,
    Hierarchy,
    HierarchyAssociation,
)
from pysdmx.model.concept import Concept, ConceptScheme, DataType, Facets
from pysdmx.model.dataflow import (
    ArrayBoundaries,
    Component,
    Components,
    Dataflow,
    DataflowInfo,
    Role,
    Schema,
)
from pysdmx.model.dataset import SeriesInfo
from pysdmx.model.map import (
    ComponentMap,
    DatePatternMap,
    FixedValueMap,
    ImplicitComponentMap,
    MultiComponentMap,
    MultiRepresentationMap,
    MultiValueMap,
    RepresentationMap,
    StructureMap,
    ValueMap,
)
from pysdmx.model.metadata import MetadataAttribute, MetadataReport
from pysdmx.model.organisation import (
    AgencyScheme,
    DataConsumerScheme,
    DataProviderScheme,
    MetadataProviderScheme,
)


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
        NotImplemented: In case the object type is not one of the types
            needing conversion
    """
    if isinstance(obj, Components):
        return list(obj)
    else:
        # Raise a NotImplemented for other types
        raise NotImplemented(
            "Unsupported", f"Objects of type {type(obj)} are not supported"
        )


def decoders(type: Type, obj: Any) -> Any:  # type: ignore[type-arg]
    """Decoders for msgspec deserialization."""
    if type is Components:
        comps = []
        for item in obj:
            comps.append(msgspec.convert(item, Component))
        return Components(comps)
    else:
        raise NotImplementedError(f"Objects of type {type} are not supported")


__all__ = [
    "Agency",
    "AgencyScheme",
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
    "DataConsumer",
    "DataConsumerScheme",
    "Dataflow",
    "DataflowInfo",
    "DataflowRef",
    "DataType",
    "DatePatternMap",
    "DataProvider",
    "DataProviderScheme",
    "Facets",
    "HierarchicalCode",
    "Hierarchy",
    "HierarchyAssociation",
    "ImplicitComponentMap",
    "StructureMap",
    "MetadataAttribute",
    "MetadataProvider",
    "MetadataProviderScheme",
    "MetadataReport",
    "MultiComponentMap",
    "MultiRepresentationMap",
    "MultiValueMap",
    "Organisation",
    "RepresentationMap",
    "Role",
    "Schema",
    "SeriesInfo",
    "ValueMap",
    "FixedValueMap",
]
