"""Collection of SDMX-JSON schemas for reference metadata queries."""

from typing import Any, Literal, Optional, Sequence

from msgspec import Struct

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.core import (
    IdentifiableType,
    ItemSchemeType,
    JsonAnnotation,
    JsonHeader,
    JsonTextFormat,
    get_facets,
)
from pysdmx.model import Agency
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
            annotations=tuple([a.to_model() for a in self.annotations]),
            format=get_facets(self.format) if self.format else None,
        )

    @classmethod
    def from_model(self, attr: MetadataAttribute) -> "JsonMetadataAttribute":
        """Converts a pysdmx metadata attribute to an SDMX-JSON one."""
        return JsonMetadataAttribute(
            id=attr.id,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in attr.annotations]
            ),
            value=attr.value,
            attributes=tuple(
                [JsonMetadataAttribute.from_model(a) for a in attr.attributes]
            ),
            format=JsonTextFormat.from_model(None, attr.format),
        )


class JsonMetadataReport(ItemSchemeType, frozen=True, omit_defaults=True):
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
            annotations=tuple([a.to_model() for a in self.annotations]),
            id=self.id,
            name=self.name,
            description=self.description,
            valid_from=self.validFrom,
            valid_to=self.validTo,
            version=self.version,
            agency=self.agency,
            is_external_reference=self.isExternalReference,
            metadataflow=self.metadataflow,
            targets=tuple(self.targets),
            attributes=tuple(attrs),
            metadataProvisionAgreement=self.metadataProvisionAgreement,
            publicationPeriod=self.publicationPeriod,
            publicationYear=self.publicationYear,
            reportingBegin=self.reportingBegin,
            reportingEnd=self.reportingEnd,
            action=ActionType(self.action) if self.action else None,
        )

    @classmethod
    def from_model(cls, report: MetadataReport) -> "JsonMetadataReport":
        """Converts a pysdmx metadata report to an SDMX-JSON one."""
        if not report.name:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON metadata reports must have a name",
                {"metadata_report": report.id},
            )

        return JsonMetadataReport(
            agency=(
                report.agency.id
                if isinstance(report.agency, Agency)
                else report.agency
            ),
            id=report.id,
            name=report.name,
            version=report.version,
            isExternalReference=report.is_external_reference,
            validFrom=report.valid_from,
            validTo=report.valid_to,
            description=report.description,
            annotations=tuple(
                [JsonAnnotation.from_model(a) for a in report.annotations]
            ),
            metadataflow=report.metadataflow,
            targets=report.targets,
            attributes=tuple(
                [
                    JsonMetadataAttribute.from_model(a)
                    for a in report.attributes
                ]
            ),
            metadataProvisionAgreement=report.metadataProvisionAgreement,
            publicationPeriod=report.publicationPeriod,
            publicationYear=report.publicationYear,
            reportingBegin=report.reportingBegin,
            reportingEnd=report.reportingEnd,
            action=report.action.value if report.action else None,
        )


class JsonMetadataSets(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for the list of metadata sets."""

    metadataSets: Sequence[JsonMetadataReport]

    def to_model(self) -> Sequence[MetadataReport]:
        """Returns the requested metadata report(s)."""
        return [r.to_model() for r in self.metadataSets]


class JsonMetadataMessage(Struct, frozen=True, omit_defaults=True):
    """SDMX-JSON payload for /metadata queries."""

    meta: JsonHeader
    data: JsonMetadataSets

    def to_model(self) -> MetadataMessage:
        """Returns the requested metadata report(s)."""
        header = self.meta.to_model()
        reports = self.data.to_model()
        return MetadataMessage(header, reports)

    @classmethod
    def from_model(
        self,
        msg: MetadataMessage,
        msg_version: Literal["2.0.0", "2.1.0"] = "2.0.0",
    ) -> "JsonMetadataMessage":
        """Converts a pysdmx metadata message to an SDMX-JSON one."""
        if not msg.header:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON metadata messages must have a header.",
            )
        if not msg.reports:
            raise errors.Invalid(
                "Invalid input",
                "SDMX-JSON metadata messages must have metadata reports.",
            )

        header = JsonHeader.from_model(msg.header, "metadata", msg_version)
        reports = [JsonMetadataReport.from_model(r) for r in msg.reports]
        return JsonMetadataMessage(header, JsonMetadataSets(reports))
