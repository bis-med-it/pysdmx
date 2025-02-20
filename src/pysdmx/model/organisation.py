"""Model for SDMX agency schemes and data provider schemes."""

from typing import Iterator, Optional, Sequence

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

    @property
    def agencies(self) -> Sequence[Agency]:
        """Extract the items in the scheme."""
        return self.items

    def __iter__(self) -> Iterator[Agency]:
        """Return an iterator over the list of agencies."""
        yield from self.items

    def __len__(self) -> int:
        """Return the number of agencies in the scheme."""
        return len(self.items)

    def __getitem__(self, id_: str) -> Optional[Agency]:
        """Return the agency identified by the supplied ID."""
        out = list(filter(lambda p: p.id == id_, self.items))
        if len(out) == 0:
            return None
        else:
            return out[0]

    def __contains__(self, id_: str) -> bool:
        """Whether an agency with the supplied ID is present in the scheme."""
        return bool(self.__getitem__(id_))


class DataProviderScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of data providers."""

    id: str = "DATA_PROVIDERS"
    name: str = "DATA_PROVIDERS"
    version: str = "1.0"
    items: Sequence[DataProvider] = ()

    @property
    def providers(self) -> Sequence[DataProvider]:
        """Extract the items in the scheme."""
        return self.items

    def __iter__(self) -> Iterator[DataProvider]:
        """Return an iterator over the list of data providers."""
        yield from self.items

    def __len__(self) -> int:
        """Return the number of data providers in the scheme."""
        return len(self.items)

    def __getitem__(self, id_: str) -> Optional[DataProvider]:
        """Return the data provider identified by the supplied ID."""
        out = list(filter(lambda p: p.id == id_, self.items))
        if len(out) == 0:
            return None
        else:
            return out[0]

    def __contains__(self, id_: str) -> bool:
        """Whether a provider with the supplied ID is present in the scheme."""
        return bool(self.__getitem__(id_))


class MetadataProviderScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of metadata providers."""

    id: str = "METADATA_PROVIDERS"
    name: str = "METADATA_PROVIDERS"
    version: str = "1.0"
    items: Sequence[MetadataProvider] = ()

    @property
    def providers(self) -> Sequence[MetadataProvider]:
        """Extract the items in the scheme."""
        return self.items

    def __iter__(self) -> Iterator[MetadataProvider]:
        """Return an iterator over the list of metadata providers."""
        yield from self.items

    def __len__(self) -> int:
        """Return the number of metadata providers in the scheme."""
        return len(self.items)

    def __getitem__(self, id_: str) -> Optional[MetadataProvider]:
        """Return the metadata provider identified by the supplied ID."""
        out = list(filter(lambda p: p.id == id_, self.items))
        if len(out) == 0:
            return None
        else:
            return out[0]

    def __contains__(self, id_: str) -> bool:
        """Whether a provider with the supplied ID is present in the scheme."""
        return bool(self.__getitem__(id_))


class DataConsumerScheme(ItemScheme, frozen=True, omit_defaults=True):
    """An immutable collection of data consumers."""

    id: str = "DATA_CONSUMERS"
    name: str = "DATA_CONSUMERS"
    version: str = "1.0"
    items: Sequence[DataConsumer] = ()

    @property
    def consumers(self) -> Sequence[DataConsumer]:
        """Extract the items in the scheme."""
        return self.items

    def __iter__(self) -> Iterator[DataConsumer]:
        """Return an iterator over the list of data consumers."""
        yield from self.items

    def __len__(self) -> int:
        """Return the number of data consumers in the scheme."""
        return len(self.items)

    def __getitem__(self, id_: str) -> Optional[DataConsumer]:
        """Return the data consumer identified by the supplied ID."""
        out = list(filter(lambda p: p.id == id_, self.items))
        if len(out) == 0:
            return None
        else:
            return out[0]

    def __contains__(self, id_: str) -> bool:
        """Whether a consumer with the supplied ID is present in the scheme."""
        return bool(self.__getitem__(id_))
