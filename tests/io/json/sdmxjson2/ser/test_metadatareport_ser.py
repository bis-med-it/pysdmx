from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.report import JsonMetadataReport
from pysdmx.model import Agency, Annotation
from pysdmx.model.dataset import ActionType
from pysdmx.model.metadata import MetadataAttribute, MetadataReport


@pytest.fixture
def metadata_report():
    attr = MetadataAttribute(
        id="ATTR1",
        value="test value",
    )
    return MetadataReport(
        id="MR1",
        name="Metadata Report",
        agency="BIS",
        description="Test metadata report",
        version="1.0",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        metadataflow="urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow=BIS:MF1(1.0)",
        targets=["TARGET1", "TARGET2"],
        attributes=[attr],
        metadataProvisionAgreement="MPA1",
        publicationPeriod="2023-Q1",
        publicationYear="2023",
        reportingBegin="2023-01-01",
        reportingEnd="2023-03-31",
        action=ActionType.Append,
    )


@pytest.fixture
def metadata_report_mult_values():
    attr = MetadataAttribute(
        id="ATTR1",
        value=["test value 1", "test value 2"],
    )
    return MetadataReport(
        id="MR1",
        name="Metadata Report",
        agency="BIS",
        description="Test metadata report",
        version="1.0",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        metadataflow="urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow=BIS:MF1(1.0)",
        targets=["TARGET1", "TARGET2"],
        attributes=[attr],
        metadataProvisionAgreement="MPA1",
        publicationPeriod="2023-Q1",
        publicationYear="2023",
        reportingBegin="2023-01-01",
        reportingEnd="2023-03-31",
        action=ActionType.Append,
    )


@pytest.fixture
def metadata_report_org():
    attr = MetadataAttribute(
        id="ATTR1",
        value="test value",
    )
    return MetadataReport(
        id="MR1",
        name="Metadata Report",
        agency=Agency("BIS"),
        attributes=[attr],
        metadataflow="urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow=BIS:MF1(1.0)",
    )


@pytest.fixture
def metadata_report_no_name():
    attr = MetadataAttribute(
        id="ATTR1",
        value="test value",
    )
    return MetadataReport(
        id="MR1",
        agency=Agency("BIS"),
        attributes=[attr],
        metadataflow="urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow=BIS:MF1(1.0)",
    )


def test_metadata_report(metadata_report: MetadataReport):
    sjson = JsonMetadataReport.from_model(metadata_report)

    assert sjson.id == metadata_report.id
    assert sjson.name == metadata_report.name
    assert sjson.agency == metadata_report.agency
    assert sjson.description == metadata_report.description
    assert sjson.version == metadata_report.version
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.validFrom == metadata_report.valid_from
    assert sjson.validTo == metadata_report.valid_to
    assert sjson.metadataflow == metadata_report.metadataflow
    assert sjson.targets == metadata_report.targets
    assert len(sjson.attributes) == 1
    for attr in sjson.attributes:
        assert attr.id == "ATTR1"
        assert attr.value == "test value"
    assert (
        sjson.metadataProvisionAgreement
        == metadata_report.metadataProvisionAgreement
    )
    assert sjson.publicationPeriod == metadata_report.publicationPeriod
    assert sjson.publicationYear == metadata_report.publicationYear
    assert sjson.reportingBegin == metadata_report.reportingBegin
    assert sjson.reportingEnd == metadata_report.reportingEnd
    assert sjson.action == metadata_report.action.value


def test_metadata_report_org(metadata_report_org: MetadataReport):
    sjson = JsonMetadataReport.from_model(metadata_report_org)

    assert sjson.agency == metadata_report_org.agency.id


def test_metadata_report_no_name(metadata_report_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonMetadataReport.from_model(metadata_report_no_name)


def test_metadata_report_multiple_values(
    metadata_report_mult_values: MetadataReport,
):
    sjson = JsonMetadataReport.from_model(metadata_report_mult_values)

    assert len(sjson.attributes) == 2
    for attr in sjson.attributes:
        assert attr.id == "ATTR1"
        assert attr.value in ["test value 1", "test value 2"]
