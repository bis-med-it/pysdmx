"""Collection of SDMX-JSON schemas for reference metadata queries."""

from typing import Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import ItemSchemeType
from pysdmx.model.dataset import ActionType
from pysdmx.model.metadata import (
    MetadataAttribute,
    MetadataReport,
    merge_attributes,
)


class JsonMetadataReport(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for a metadata report."""

    metadataflow: str = ""
    targets: Sequence[str] = ()
    attributes: Sequence[MetadataAttribute] = ()
    metadataProvisionAgreement: Optional[str] = None
    publicationPeriod: Optional[str] = None
    publicationYear: Optional[str] = None
    reportingBegin: Optional[str] = None
    reportingEnd: Optional[str] = None
    action: Optional[str] = None

    def to_model(self) -> MetadataReport:
        """Converts a JsonMetadataReport to a standard report."""
        attrs = merge_attributes(self.attributes)
        return MetadataReport(
            annotations=[a.to_model() for a in self.annotations],
            id=self.id,
            name=self.name,
            description=self.description,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            version=self.version,
            agency=self.agency,
            is_external_reference=self.isExternalReference,
            metadataflow=self.metadataflow,
            targets=self.targets,
            attributes=attrs,
            metadataProvisionAgreement=self.metadataProvisionAgreement,
            publicationPeriod=self.publicationPeriod,
            publicationYear=self.publicationYear,
            reportingBegin=self.reportingBegin,
            reportingEnd=self.reportingEnd,
            action=ActionType(self.action) if self.action else None,
        )


class JsonMetadataSets(Struct, frozen=True):
    """SDMX-JSON payload for the list of metadata sets."""

    metadataSets: Sequence[JsonMetadataReport]

    def to_model(self) -> Sequence[MetadataReport]:
        """Returns the requested metadata report(s)."""
        return [r.to_model() for r in self.metadataSets]


class JsonMetadataMessage(Struct, frozen=True):
    """SDMX-JSON payload for /metadata queries."""

    data: JsonMetadataSets

    def to_model(self, fetch_all: bool = False) -> Sequence[MetadataReport]:
        """Returns the requested metadata report(s)."""
        reports = self.data.to_model()
        if fetch_all:
            return reports
        else:
            return [reports[0]]
