"""Tests for writing SDMX-ML 3.0 reference metadata (GenericMetadata)."""

from datetime import datetime
from pathlib import Path

import pytest

from pysdmx.errors import Invalid
from pysdmx.io import write_sdmx
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.reader import read_sdmx
from pysdmx.io.xml.sdmx30.writer.metadata import write
from pysdmx.model import MetadataStructure
from pysdmx.model.dataset import ActionType
from pysdmx.model.message import Header, Organisation
from pysdmx.model.metadata import MetadataAttribute, MetadataReport

MDF_URN = (
    "urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow=BIS:MDF(1.0)"
)
DF_TARGET = "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS:DF(1.0)"


@pytest.fixture
def complete_header():
    return Header(
        id="ID",
        prepared=datetime.strptime("2021-01-01", "%Y-%m-%d"),
        sender=Organisation(id="ZZZ"),
    )


@pytest.fixture
def report():
    return MetadataReport(
        id="RPT1",
        name="Report 1",
        agency="BIS",
        version="1.0",
        metadataflow=MDF_URN,
        targets=(DF_TARGET,),
        action=ActionType.Replace,
        publicationYear="2021",
        publicationPeriod="2021-Q1",
        reportingBegin="2020-01-01",
        reportingEnd="2020-12-31",
        attributes=(
            MetadataAttribute(
                id="CONTACT",
                attributes=(
                    MetadataAttribute(id="NAME", value="John Doe"),
                    MetadataAttribute(
                        id="EMAIL",
                        value=["a@example.org", "b@example.org"],
                    ),
                ),
            ),
            MetadataAttribute(id="NOTE", value="A single note"),
        ),
    )


@pytest.fixture
def samples_folder():
    return Path(__file__).parent.parent / "reader" / "samples"


@pytest.mark.xml
def test_generic_metadata_substrings_30(complete_header, report):
    result = write([report], header=complete_header, prettyprint=True)
    # MetadataSet element (NOT MetadataReport)
    assert "<mes:MetadataSet" in result
    assert "<mes:GenericMetadata" in result
    # reportingBegin / reportingEnd map to reportingBeginDate/EndDate
    assert 'reportingBeginDate="2020-01-01"' in result
    assert 'reportingEndDate="2020-12-31"' in result
    assert 'publicationYear="2021"' in result
    assert 'publicationPeriod="2021-Q1"' in result
    assert 'action="Replace"' in result
    assert "<metadata:Metadataflow>" in result
    # List value expands into repeated attributes
    assert result.count('<metadata:Attribute id="EMAIL">') == 2
    _, read_format = process_string_to_read(result)
    assert read_format == Format.REFMETA_SDMX_ML_3_0


@pytest.mark.xml
def test_generic_metadata_round_trip_30(samples_folder):
    # Read -> write -> read must preserve the reports exactly. Reading first
    # gives the canonical model shape (merge_attributes normalisation).
    data_path = samples_folder / "generic_metadata.xml"
    reports = read_sdmx(str(data_path), validate=True).get_reports()
    result = write(reports, prettyprint=True)
    re_read = read_sdmx(result, validate=True).get_reports()
    assert list(re_read) == list(reports)


@pytest.mark.xml
def test_generic_metadata_no_header_30(samples_folder):
    # The header (with its required <mes:Structure>) is synthesized from the
    # report's metadataflow when none is supplied.
    data_path = samples_folder / "generic_metadata.xml"
    reports = read_sdmx(str(data_path), validate=True).get_reports()
    result = write(reports, prettyprint=True)
    assert "<mes:Structure structureID=" in result
    assert "<com:StructureUsage>" in result
    re_read = read_sdmx(result, validate=True).get_reports()
    assert list(re_read) == list(reports)


@pytest.mark.xml
def test_generic_metadata_mpa_choice_30(complete_header):
    report = MetadataReport(
        id="RPT_MPA",
        name="Report via MPA",
        agency="BIS",
        version="1.0",
        metadataProvisionAgreement=(
            "urn:sdmx:org.sdmx.infomodel.registry."
            "MetadataProvisionAgreement=BIS:MPA(1.0)"
        ),
        targets=(DF_TARGET,),
        attributes=(MetadataAttribute(id="NOTE", value="A note"),),
    )
    # An MPA-only report needs a header structure (cannot be derived from a
    # metadataflow). Supply a metadata structure reference.
    header = Header(
        structure={"MetadataStructure=BIS:MSD(1.0)": "AllDimensions"}
    )
    result = write([report], header=header, prettyprint=True)
    assert "<metadata:MetadataProvisionAgreement>" in result
    assert "<com:Structure>" in result
    re_read = read_sdmx(result, validate=True).get_reports()
    assert list(re_read) == [report]


@pytest.mark.xml
def test_generic_metadata_neither_flow_nor_mpa_raises():
    # The XSD requires a MetadataSet to reference a metadataflow or an MPA.
    report = MetadataReport(
        id="RPT",
        name="No flow nor MPA",
        agency="BIS",
        version="1.0",
        targets=(DF_TARGET,),
        attributes=(MetadataAttribute(id="NOTE", value="x"),),
    )
    header = Header(
        structure={"MetadataStructure=BIS:MSD(1.0)": "AllDimensions"}
    )
    with pytest.raises(
        Invalid, match="metadataflow or a metadata provision agreement"
    ):
        write([report], header=header, prettyprint=True)


@pytest.mark.xml
def test_generic_metadata_no_metadataflow_raises():
    # No metadataflow and no header -> cannot build the required header.
    report = MetadataReport(
        id="RPT", name="No flow", agency="BIS", version="1.0"
    )
    with pytest.raises(Invalid, match="metadataflow reference"):
        write([report], prettyprint=True)


@pytest.mark.xml
def test_generic_metadata_no_name_raises(complete_header):
    report = MetadataReport(
        id="RPT", agency="BIS", version="1.0", metadataflow=MDF_URN
    )
    with pytest.raises(Invalid, match="must have a name"):
        write([report], header=complete_header, prettyprint=True)


@pytest.mark.xml
def test_write_non_report_raises():
    msd = MetadataStructure(id="M", name="n", agency="A", version="1.0")
    with pytest.raises(Invalid, match="metadata reports"):
        write_sdmx([msd], Format.REFMETA_SDMX_ML_3_0)


@pytest.mark.xml
def test_generic_metadata_output_path(samples_folder, tmp_path):
    data_path = samples_folder / "generic_metadata.xml"
    reports = read_sdmx(str(data_path), validate=True).get_reports()
    output_path = str(tmp_path / "out.xml")
    result = write(reports, output_path=output_path)
    assert result is None
    re_read = read_sdmx(output_path, validate=True).get_reports()
    assert list(re_read) == list(reports)
