"""Model for SDMX agency schemes and data provider schemes."""

from typing import Sequence

from pysdmx.model.__base import (
    Agency,
    DataConsumer,
    DataProvider,
    ItemScheme,
    MetadataProvider,
)


class AgencyScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of agencies."""

    id: str = "AGENCIES"
    name: str = "AGENCIES"
    version: str = "1.0"
    items: Sequence[Agency] = ()


class DataProviderScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of data providers."""

    id: str = "DATA_PROVIDERS"
    name: str = "DATA_PROVIDERS"
    version: str = "1.0"
    items: Sequence[DataProvider] = ()


class MetadataProviderScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of metadata providers."""

    id: str = "METADATA_PROVIDERS"
    name: str = "METADATA_PROVIDERS"
    version: str = "1.0"
    items: Sequence[MetadataProvider] = ()


class DataConsumerScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of data consumers."""

    id: str = "DATA_CONSUMERS"
    name: str = "DATA_CONSUMERS"
    version: str = "1.0"
    items: Sequence[DataConsumer] = ()
