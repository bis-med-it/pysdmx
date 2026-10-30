from importlib.util import find_spec
from pathlib import Path

import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.json.sdmxjson2.reader.metadata import read as read_metadata
from pysdmx.io.json.sdmxjson2.reader.structure import read as read_structure

# The noextra CI job runs these tests without any extra installed. SDMX-JSON
# messages must be readable without validation (issue #719), while validating
# them, or reading SDMX-ML messages, must point to the missing extra.

SAMPLES = Path(__file__).parent / "samples"
FMR_SAMPLES = Path(__file__).parent.parent / "api" / "fmr" / "samples"
JSON_STRUCTURE = FMR_SAMPLES / "code" / "freq.json"
JSON_REFMETA = FMR_SAMPLES / "refmeta" / "report.json"
JSON_EXTRA = all(
    find_spec(name)
    for name in ("jsonschema", "rfc3339_validator", "sdmxschemas")
)
XML_EXTRA = all(
    find_spec(name) for name in ("lxml", "sdmxschemas", "xmltodict")
)


@pytest.mark.parametrize("file_name", ["freq.json", "freq_21.json"])
def test_read_json_structure_without_validation(file_name):
    msg = read_sdmx(FMR_SAMPLES / "code" / file_name, validate=False)

    assert [cl.short_urn for cl in msg.get_codelists()] == [
        "Codelist=SDMX:CL_FREQ(2.0)"
    ]


@pytest.mark.parametrize("file_name", ["report.json", "report_21.json"])
def test_read_json_refmeta_without_validation(file_name):
    msg = read_sdmx(FMR_SAMPLES / "refmeta" / file_name, validate=False)

    assert [r.id for r in msg.reports] == ["DTI_BIS_MACRO"]


def test_json_structure_reader_without_validation():
    text = JSON_STRUCTURE.read_text(encoding="utf-8")

    msg = read_structure(text, validate=False)

    assert [cl.short_urn for cl in msg.get_codelists()] == [
        "Codelist=SDMX:CL_FREQ(2.0)"
    ]


def test_json_metadata_reader_without_validation():
    text = JSON_REFMETA.read_text(encoding="utf-8")

    msg = read_metadata(text, validate=False)

    assert [r.id for r in msg.reports] == ["DTI_BIS_MACRO"]


@pytest.mark.skipif(JSON_EXTRA, reason="the json extra is installed")
def test_json_validation_requires_json_extra():
    with pytest.raises(ImportError, match="'json' extra is required"):
        read_sdmx(JSON_STRUCTURE, validate=True)


@pytest.mark.skipif(XML_EXTRA, reason="the xml extra is installed")
@pytest.mark.parametrize("validate", [True, False])
def test_xml_reading_requires_xml_extra(validate):
    with pytest.raises(ImportError, match="'xml' extra is required"):
        read_sdmx(SAMPLES / "valid.xml", validate=validate)
