from datetime import datetime

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.report import (
    JsonMetadataMessage,
    JsonMetadataReport,
)
from pysdmx.model import MetadataAttribute, MetadataReport, Organisation
from pysdmx.model.dataset import ActionType
from pysdmx.model.message import Header, MetadataMessage


@pytest.fixture
def header():
    return Header(id="test42", test=True, sender=Organisation("BIS"))


@pytest.fixture
def report():
    attr = MetadataAttribute(
        id="ATTR1",
        value="test value",
    )
    return MetadataReport(
        id="MR1",
        name="Metadata Report",
        agency="BIS",
        version="1.0",
        metadataflow="urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow=BIS:MF1(1.0)",
        targets=["TARGET1", "TARGET2"],
        attributes=[attr],
        metadataProvisionAgreement="MPA1",
        action=ActionType.Append,
    )


@pytest.fixture
def msg(header, report):
    return MetadataMessage(header, [report])


def test_metadata_report(msg: MetadataMessage):
    sjson = JsonMetadataMessage.from_model(msg)

    # Check header
    assert sjson.meta is not None
    assert sjson.meta.id == "test42"
    assert sjson.meta.test is True
    assert sjson.meta.sender.id == "BIS"
    assert isinstance(sjson.meta.prepared, datetime)

    # Check content
    assert len(sjson.data.metadataSets) == 1
    assert isinstance(sjson.data.metadataSets[0], JsonMetadataReport)


def test_no_header(report):
    msg = MetadataMessage(None, [report])

    with pytest.raises(
        errors.Invalid, match="metadata messages must have a header"
    ):
        JsonMetadataMessage.from_model(msg)


def test_no_report(header):
    msg = MetadataMessage(header, [])

    with pytest.raises(
        errors.Invalid, match="metadata messages must have metadata reports"
    ):
        JsonMetadataMessage.from_model(msg)
