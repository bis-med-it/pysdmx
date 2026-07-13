import json
from pathlib import Path

from sdmxschemas import (
    SDMX_JSON_20_STRUCTURE_PATH,
    SDMX_JSON_21_STRUCTURE_PATH,
)

from pysdmx.io.json.sdmxjson2.reader.doc_validation import _schema_for
from pysdmx.io.json.sdmxjson2.reader.structure import read as read_structure

# A real, valid SDMX-JSON 2.1 structure message.
FREQ_21 = (
    Path(__file__).parents[4]
    / "api"
    / "fmr"
    / "samples"
    / "code"
    / "freq_21.json"
)


def _load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def test_schema_for_selects_21_structure():
    url = "https://json.sdmx.org/2.1/sdmx-json-structure-schema.json"
    schema = _schema_for({"meta": {"schema": url}})
    assert schema == _load(SDMX_JSON_21_STRUCTURE_PATH)


def test_schema_for_selects_20_structure():
    url = "https://json.sdmx.org/2.0.0/sdmx-json-structure-schema.json"
    schema = _schema_for({"meta": {"schema": url}})
    assert schema == _load(SDMX_JSON_20_STRUCTURE_PATH)


def test_21_structure_validates_against_21_schema():
    # A real 2.1 message must validate against the 2.1 schema. Its ``prepared``
    # is a date-time; the 2.1 schema types it as ``oneOf(date-time, date)``,
    # which only resolves correctly because the format checker is enabled.
    text = FREQ_21.read_text(encoding="utf-8")
    assert read_structure(text, validate=True) is not None
