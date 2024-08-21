from io import BytesIO
from pathlib import Path

import pytest

from pysdmx.io.input_processor import process_string_to_read
from pysdmx.io.xml.sdmx21.reader import read_xml


@pytest.fixture()
def valid_xml_path():
    return Path(__file__).parent / "samples" / "valid.xml"


@pytest.fixture()
def valid_xml_bytes(valid_xml):
    return BytesIO(valid_xml.encode("utf-8"))


@pytest.fixture()
def valid_xml():
    path = Path(__file__).parent / "samples" / "valid.xml"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture()
def valid_xml_bom():
    path = Path(__file__).parent / "samples" / "valid_bom.xml"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture()
def invalid_xml():
    path = Path(__file__).parent / "samples" / "invalid.xml"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture()
def invalid_message_xml():
    path = Path(__file__).parent / "samples" / "invalid_message.xml"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_process_string_to_read(valid_xml, valid_xml_path):
    infile, filetype = process_string_to_read(valid_xml_path)
    assert infile == valid_xml
    assert filetype == "xml"


def test_process_string_to_read_bytes(valid_xml, valid_xml_bytes):
    infile, filetype = process_string_to_read(valid_xml_bytes)
    assert infile == valid_xml
    assert filetype == "xml"


def test_process_string_to_read_str(valid_xml):
    infile, filetype = process_string_to_read(valid_xml)
    assert infile == valid_xml
    assert filetype == "xml"


def test_process_string_to_read_bom(valid_xml, valid_xml_bom):
    infile, filetype = process_string_to_read(valid_xml_bom)
    assert infile[:5] == "<?xml"
    assert filetype == "xml"


def test_process_string_to_read_invalid_xml(invalid_xml):
    message = "This element is not expected."
    process_string_to_read(invalid_xml)
    with pytest.raises(ValueError, match=message):
        read_xml(invalid_xml, validate=True)


def test_process_string_to_read_invalid_type():
    message = "Cannot parse input of type"
    with pytest.raises(ValueError, match=message):
        process_string_to_read(123)


def test_process_string_to_read_invalid_path():
    message = "No such file or directory"
    with pytest.raises(FileNotFoundError, match=message):
        process_string_to_read(Path("invalid_eee.xml"))


def test_process_string_to_read_valid_json():
    infile, filetype = process_string_to_read('{"key": "value"}')
    assert infile == '{"key": "value"}'
    assert filetype == "json"


def test_process_string_to_read_invalid_json():
    with pytest.raises(ValueError, match="Cannot parse input as SDMX."):
        process_string_to_read('{"key": "value"')


def test_process_string_to_read_invalid_allowed_error(invalid_message_xml):
    message = "Cannot parse input as SDMX."
    with pytest.raises(ValueError, match=message):
        read_xml(invalid_message_xml, validate=False)
