"""Collection of SDMX-JSON schemas for reference metadata queries."""

from typing import Any, Optional, Sequence

from msgspec import Struct

from pysdmx.io.json.sdmxjson2.messages.core import (
    IdentifiableType,
    ItemSchemeType,
    JsonHeader,
    JsonTextFormat,
    get_facets,
)
from pysdmx.model.dataset import ActionType
from pysdmx.model.message import MetadataMessage
from pysdmx.model.metadata import (
    MetadataAttribute,
    MetadataReport,
    merge_attributes,
)


class JsonMetadataAttribute(IdentifiableType, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for a metadata attribute."""

    value: Optional[Any] = None
    attributes: Sequence["JsonMetadataAttribute"] = ()
    format: Optional[JsonTextFormat] = None

    def to_model(self) -> MetadataAttribute:
        """Converts a JsonMetadataAttribute to a standard attribute."""
        attrs = [a.to_model() for a in self.attributes]
        attrs = merge_attributes(attrs)  # type: ignore[assignment]
        return MetadataAttribute(
            id=self.id,
            value=self.value,
            attributes=attrs,
            annotations=[a.to_model() for a in self.annotations],
            format=get_facets(self.format) if self.format else None,
        )


class JsonMetadataReport(ItemSchemeType, frozen=True):
    """SDMX-JSON payload for a metadata report."""

    metadataflow: str = ""
    targets: Sequence[str] = ()
    attributes: Sequence[JsonMetadataAttribute] = ()
    metadataProvisionAgreement: Optional[str] = None
    publicationPeriod: Optional[str] = None
    publicationYear: Optional[str] = None
    reportingBegin: Optional[str] = None
    reportingEnd: Optional[str] = None
    action: Optional[str] = None

    def to_model(self) -> MetadataReport:
        """Converts a JsonMetadataReport to a standard report."""
        attrs = [a.to_model() for a in self.attributes]
        attrs = merge_attributes(attrs)  # type: ignore[assignment]
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

    meta: JsonHeader
    data: JsonMetadataSets

    def to_model(self) -> MetadataMessage:
        """Returns the requested metadata report(s)."""
        header = self.meta.to_model()
        reports = self.data.to_model()
        return MetadataMessage(header, reports)
