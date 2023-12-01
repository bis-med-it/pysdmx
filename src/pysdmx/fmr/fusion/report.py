"""Collection of Fusion-JSON schemas for reference metadata queries."""

from typing import Sequence

from msgspec import Struct

from pysdmx.fmr.fusion.core import FusionString
from pysdmx.fmr.reader import _merge_attributes
from pysdmx.model import MetadataAttribute, MetadataReport


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

    def to_model(self) -> MetadataReport:
        """Returns the requested metadata report."""
        r = self.data.metadatasets[0]
        attrs = _merge_attributes(r.attributes)
        return MetadataReport(
            r.id, r.names[0].value, r.metadataflow, r.targets, attrs
        )
