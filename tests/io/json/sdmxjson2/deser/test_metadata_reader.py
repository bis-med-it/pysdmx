import msgspec
import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages import JsonMetadataMessage
from pysdmx.io.json.sdmxjson2.reader.metadata import read
from pysdmx.model.message import MetadataMessage


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/reports/report.json", "rb"
    ) as f:
        return f.read()


@pytest.fixture
def empty():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/reports/no_report.json", "rb"
    ) as f:
        return f.read()


def test_metadata_reader(body):
    res = msgspec.json.Decoder(JsonMetadataMessage).decode(body)
    msg = res.to_model()

    assert isinstance(msg, MetadataMessage)

    assert len(msg.get_reports()) == 1


def test_empty_metadata_reader(empty):
    res = msgspec.json.Decoder(JsonMetadataMessage).decode(empty)
    msg = res.to_model()

    assert isinstance(msg, MetadataMessage)

    with pytest.raises(errors.NotFound):
        msg.get_reports()


def test_get_json2_invalid_refmeta():
    with pytest.raises(
        errors.Invalid,
        match="as SDMX-JSON 2.0.0 or 2.1.0 reference metadata message.",
    ):
        read("pyproject.toml", validate=False)
