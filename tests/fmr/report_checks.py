import httpx
import pytest

from pysdmx.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import MetadataAttribute, MetadataReport


def check_report(mock, fmr: RegistryClient, query, body):
    """get_report() should return a metadata report."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    report = fmr.get_report("BIS.MEDIT", "DTI_BIS_MACRO", "1.0")

    assert isinstance(report, MetadataReport)
    assert report.id == "DTI_BIS_MACRO"
    assert report.name == "Technical metadata for BIS.MACRO:BIS_MACRO"
    assert report.metadataflow == (
        "urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow="
        "BIS.MEDIT:DTI(1.0)"
    )
    assert len(report.targets) == 1
    assert "Dataflow=BIS.MACRO:BIS_MACRO(1.0)" in report.targets[0]
    assert len(report) == 5
    for attr in report:
        assert isinstance(attr, MetadataAttribute)


async def check_attributes(mock, fmr: AsyncRegistryClient, query, body):
    """Attributes contain the expected information."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    report = await fmr.get_report("BIS.MEDIT", "DTI_BIS_MACRO", "1.0")

    for attr in report:
        if attr.id == "idea_partition_details":
            assert attr.value is None
            assert len(attr.attributes) == 3
            for child in attr.attributes:
                if child.id == "idea_partition_name":
                    assert child.value == "dt"
                elif child.id == "idea_partition_pattern":
                    assert child.value == "\\d{4}-(0\\d|1[012])"
                elif child.id == "idea_partition_type":
                    assert child.value == "string"
                else:
                    pytest.fail(f"Unexpected attribute: {child.id}")
        elif attr.id == "record_format":
            assert attr.value == "A"
            assert len(attr.attributes) == 0
        else:
            pytest.fail(f"Unexpected attribute: {attr.id}")
