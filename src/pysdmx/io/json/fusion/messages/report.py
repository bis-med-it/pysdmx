"""Collection of Fusion-JSON schemas for reference metadata queries."""

from typing import Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.model.metadata import (
    merge_attributes,
    MetadataAttribute,
    MetadataReport,
)


class FusionMetadataReport(Struct, frozen=True):
    """Fusion-JSON payload for a metadata report."""

    id: str
    names: Sequence[FusionString]
    metadataflow: str
    targets: Sequence[str]
    attributes: Sequence[MetadataAttribute]


class FusionMetadataSets(Struct, frozen=True):
    """Fusion-JSON payload for the list of metadata sets."""

    metadatasets: Sequence[FusionMetadataReport]


class FusionMetadataMessage(Struct, frozen=True):
    """Fusion-JSON payload for /metadata queries."""

    data: FusionMetadataSets

    def __create_report(self, r: FusionMetadataReport) -> MetadataReport:
        attrs = merge_attributes(r.attributes)
        return MetadataReport(
            r.id, r.names[0].value, r.metadataflow, r.targets, attrs
        )

    def to_model(self, fetch_all: bool = False) -> Sequence[MetadataReport]:
        """Returns the requested metadata report(s)."""
        if fetch_all:
            return [self.__create_report(r) for r in self.data.metadatasets]
        else:
            return [self.__create_report(self.data.metadatasets[0])]
