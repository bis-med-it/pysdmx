"""Collection of Fusion-JSON schemas for reference metadata queries."""

from typing import Sequence

from msgspec import Struct

from pysdmx.io.json.fusion.messages.core import FusionString
from pysdmx.model.message import MetadataMessage
from pysdmx.model.metadata import (
    MetadataAttribute,
    MetadataReport,
    merge_attributes,
)


class FusionMetadataReport(Struct, frozen=True, rename={"agency": "agencyId"}):
    """Fusion-JSON payload for a metadata report."""

    id: str
    agency: str
    names: Sequence[FusionString]
    metadataflow: str
    targets: Sequence[str]
    attributes: Sequence[MetadataAttribute]
    version: str


class FusionMetadataSets(Struct, frozen=True):
    """Fusion-JSON payload for the list of metadata sets."""

    metadatasets: Sequence[FusionMetadataReport]


class FusionMetadataMessage(Struct, frozen=True):
    """Fusion-JSON payload for /metadata queries."""

    data: FusionMetadataSets

    def __create_report(self, r: FusionMetadataReport) -> MetadataReport:
        attrs = merge_attributes(r.attributes)
        return MetadataReport(
            id=r.id,
            name=r.names[0].value,
            agency=r.agency,
            metadataflow=r.metadataflow,
            targets=r.targets,
            attributes=attrs,
            version=r.version,
        )

    def to_model(self) -> MetadataMessage:
        """Returns the requested metadata report(s)."""
        reports = [self.__create_report(r) for r in self.data.metadatasets]
        return MetadataMessage(reports=reports)
