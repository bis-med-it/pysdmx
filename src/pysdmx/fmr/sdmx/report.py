"""Collection of SDMX-JSON schemas for reference metadata queries."""

from typing import Sequence

from msgspec import Struct

from pysdmx.model import MetadataReport


class JsonMetadataSets(Struct, frozen=True):
    """SDMX-JSON payload for the list of metadata sets."""

    metadataSets: Sequence[MetadataReport]


class JsonMetadataMessage(Struct, frozen=True):
    """SDMX-JSON payload for /metadata queries."""

    data: JsonMetadataSets

    def to_model(self) -> MetadataReport:
        """Returns the requested metadata report."""
        return self.data.metadataSets[0]
