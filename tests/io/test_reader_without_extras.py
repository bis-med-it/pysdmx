from importlib.util import find_spec
from pathlib import Path

import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.json.sdmxjson2.reader.metadata import read as read_metadata
from pysdmx.io.json.sdmxjson2.reader.structure import read as read_structure

# The noextra CI job runs these tests without any extra installed. SDMX-JSON
# messages must be readable without validation (issue #719), while validating
# them, or reading SDMX-ML messages, must point to the missing extra. The
# SDMX-JSON messages are the constructed samples of the official SDMX-JSON
# repository (https://github.com/sdmx-twg/sdmx-json).

SAMPLES = Path(__file__).parent / "samples"
JSON_STRUCTURE = SAMPLES / "structure_message_20.json"
JSON_REFMETA = SAMPLES / "refmeta_message_20.json"
JSON_EXTRA = all(
    find_spec(name)
    for name in ("jsonschema", "rfc3339_validator", "sdmxschemas")
)
XML_EXTRA = all(
    find_spec(name) for name in ("lxml", "sdmxschemas", "xmltodict")
)


def test_read_json_structure_without_validation():
    msg = read_sdmx(JSON_STRUCTURE, validate=False)

    assert [df.short_urn for df in msg.get_dataflows()] == [
        "Dataflow=ECB:EXR(1.0)"
    ]


@pytest.mark.parametrize(
    "file_name", ["refmeta_message_20.json", "refmeta_message_21.json"]
)
def test_read_json_refmeta_without_validation(file_name):
    msg = read_sdmx(SAMPLES / file_name, validate=False)

    assert [r.id for r in msg.reports] == [
        "METADATASET1",
        "META_UPDATE",
        "STAT_PRES",
    ]


def test_json_structure_reader_without_validation():
    text = JSON_STRUCTURE.read_text(encoding="utf-8")

    msg = read_structure(text, validate=False)

    assert [df.short_urn for df in msg.get_dataflows()] == [
        "Dataflow=ECB:EXR(1.0)"
    ]


def test_json_metadata_reader_without_validation():
    text = JSON_REFMETA.read_text(encoding="utf-8")

    msg = read_metadata(text, validate=False)

    assert [r.id for r in msg.reports] == [
        "METADATASET1",
        "META_UPDATE",
        "STAT_PRES",
    ]


@pytest.mark.skipif(JSON_EXTRA, reason="the json extra is installed")
def test_json_validation_requires_json_extra():
    with pytest.raises(ImportError, match="'json' extra is required"):
        read_sdmx(JSON_STRUCTURE, validate=True)


@pytest.mark.skipif(XML_EXTRA, reason="the xml extra is installed")
@pytest.mark.parametrize("validate", [True, False])
def test_xml_reading_requires_xml_extra(validate):
    with pytest.raises(ImportError, match="'xml' extra is required"):
        read_sdmx(SAMPLES / "valid.xml", validate=validate)
