"""Collection of SDMX-JSON schemas for reference metadata queries."""

from typing import Sequence

from msgspec import Struct

from pysdmx.model.metadata import merge_attributes, MetadataReport


class JsonMetadataSets(Struct, frozen=True):
    """SDMX-JSON payload for the list of metadata sets."""

    metadataSets: Sequence[MetadataReport]


class JsonMetadataMessage(Struct, frozen=True):
    """SDMX-JSON payload for /metadata queries."""

    data: JsonMetadataSets

    def __create_report(self, r: MetadataReport) -> MetadataReport:
        attrs = merge_attributes(r.attributes)
        return MetadataReport(r.id, r.name, r.metadataflow, r.targets, attrs)

    def to_model(self, fetch_all: bool = False) -> Sequence[MetadataReport]:
        """Returns the requested metadata report(s)."""
        if fetch_all:
            return [self.__create_report(r) for r in self.data.metadataSets]
        else:
            return [self.__create_report(self.data.metadataSets[0])]
