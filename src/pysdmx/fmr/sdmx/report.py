"""Collection of SDMX-JSON schemas for reference metadata queries."""

from typing import Sequence

from msgspec import Struct

from pysdmx.fmr.reader import _merge_attributes
from pysdmx.model import MetadataReport


class JsonMetadataSets(Struct, frozen=True):
    """SDMX-JSON payload for the list of metadata sets."""

    metadataSets: Sequence[MetadataReport]


class JsonMetadataMessage(Struct, frozen=True):
    """SDMX-JSON payload for /metadata queries."""

    data: JsonMetadataSets

    def to_model(self) -> MetadataReport:
        """Returns the requested metadata report."""
        r = self.data.metadataSets[0]
        attrs = _merge_attributes(r.attributes)
        return MetadataReport(r.id, r.name, r.metadataflow, r.targets, attrs)
