import csv
import gzip
import json
from io import BytesIO
from pathlib import Path

import httpx
import pandas as pd
import pytest

from pysdmx.errors import Invalid, NotImplemented
from pysdmx.io import input_processor
from pysdmx.io.format import Format
from pysdmx.io.input_processor import process_string_to_read, stream_sdmx
from pysdmx.io.reader import read_sdmx
from tests.io.byte_chunks import ByteChunks, split

SAMPLES = Path(__file__).parent / "samples"
DATA_SAMPLE = Path(__file__).parent / "xml/sdmx21/reader/samples/str_ser.xml"
URL = "https://sdmx.example.org/data"
CSV_SAMPLE = SAMPLES / "data_v1.csv"


@pytest.fixture
def valid_xml_path():
    return Path(__file__).parent / "samples" / "valid.xml"


@pytest.fixture
def valid_xml_bytes(valid_xml):
    return BytesIO(valid_xml.encode("utf-8"))


@pytest.fixture
def valid_xml():
    path = Path(__file__).parent / "samples" / "valid.xml"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def valid_xml_bom():
    path = Path(__file__).parent / "samples" / "valid_bom.xml"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def invalid_xml():
    path = Path(__file__).parent / "samples" / "invalid.xml"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def invalid_message_xml():
    path = Path(__file__).parent / "samples" / "invalid_message.xml"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def one_line_jsondata():
    path = Path(__file__).parent / "samples" / "one_line_jsondata.json"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def structure_json():
    path = Path(__file__).parent / "samples" / "bis_der.json"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def large_csv_1():
    path = Path(__file__).parent / "samples" / "large_csv_1.csv"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


@pytest.fixture
def large_csv_2():
    path = Path(__file__).parent / "samples" / "large_csv_2.csv"
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def test_process_string_to_read(valid_xml, valid_xml_path):
    infile, read_format = process_string_to_read(valid_xml_path)
    assert infile == valid_xml
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1


def test_process_string_to_read_bytes(valid_xml, valid_xml_bytes):
    infile, read_format = process_string_to_read(valid_xml_bytes)
    assert infile == valid_xml
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1


def test_process_string_to_read_str(valid_xml):
    infile, read_format = process_string_to_read(valid_xml)
    assert infile == valid_xml
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1


def test_process_string_to_read_str_path(valid_xml, valid_xml_path):
    infile, read_format = process_string_to_read(str(valid_xml_path))
    assert infile == valid_xml
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1


def test_process_string_to_read_bom(valid_xml, valid_xml_bom):
    infile, read_format = process_string_to_read(valid_xml_bom)
    assert infile[:5] == "<?xml"
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1


def test_process_string_to_read_invalid_xml(invalid_xml):
    message = "This element is not expected."
    process_string_to_read(invalid_xml)
    with pytest.raises(Invalid, match=message):
        read_sdmx(invalid_xml, validate=True)


def test_process_string_to_read_invalid_type():
    message = "Cannot parse input of type"
    with pytest.raises(Invalid, match=message):
        process_string_to_read(123)


def test_process_string_to_read_invalid_path():
    message = "No such file or directory"
    with pytest.raises(FileNotFoundError, match=message):
        process_string_to_read(Path("invalid_eee.xml"))


def test_process_string_to_read_valid_json():
    with pytest.raises(Invalid, match="Cannot parse input as SDMX-JSON."):
        process_string_to_read('{"key": "value"}')


def test_process_string_to_read_invalid_json():
    with pytest.raises(Invalid, match="Cannot parse input as SDMX."):
        process_string_to_read('{"key": "value"')


def test_check_csv_exception():
    with pytest.raises(Invalid):
        process_string_to_read("")


def test_process_string_to_read_invalid_allowed_error(invalid_message_xml):
    message = "Cannot parse input as SDMX-ML."
    with pytest.raises(Invalid, match=message):
        read_sdmx(invalid_message_xml, validate=False)


def test_invalid_xml_flavour():
    with pytest.raises(Invalid):
        process_string_to_read("<?xmlAAAA")


def test_process_string_to_read_one_line_json_data(one_line_jsondata):
    # Issue #658: a one-line SDMX-JSON message has enough commas and
    # quotes to be misdetected as SDMX-CSV
    assert "\n" not in one_line_jsondata.strip()
    with pytest.raises(
        NotImplemented,
        match="This flavour of SDMX-JSON is not supported.",
    ):
        process_string_to_read(one_line_jsondata)


def test_process_string_to_read_one_line_json_structure(structure_json):
    one_line = json.dumps(json.loads(structure_json))
    infile, read_format = process_string_to_read(one_line)
    assert infile == one_line
    assert read_format == Format.STRUCTURE_SDMX_JSON_2_0_0


def test_process_string_to_read_one_line_xml_no_declaration():
    # XML without the optional <?xml declaration must not be
    # misdetected as SDMX-CSV either
    one_line = (
        '<mes:Structure xmlns:mes="http://www.sdmx.org/resources/'
        'sdmxml/schemas/v2_1/message">'
        '<Name xml:lang="en">Euro, US dollar, yen</Name>'
        "</mes:Structure>"
    )
    with pytest.raises(Invalid, match=r"Cannot parse input as SDMX\.$"):
        process_string_to_read(one_line)


def test_process_string_to_read_single_line_one_comma():
    # Sniffs as CSV dialect, but a single line with a single comma is
    # not enough to be considered SDMX-CSV
    with pytest.raises(Invalid, match=r"Cannot parse input as SDMX\.$"):
        process_string_to_read('"a","b"')


def test_process_large_csv(large_csv_1, large_csv_2):
    infile, read_format = process_string_to_read(large_csv_1)
    assert infile == large_csv_1
    assert read_format == Format.DATA_SDMX_CSV_1_0_0

    infile, read_format = process_string_to_read(large_csv_2)
    assert infile == large_csv_2
    assert read_format == Format.DATA_SDMX_CSV_2_1_0


def _source(path, kind):
    if kind == "path":
        return path
    if kind == "path_str":
        return str(path)
    if kind == "text":
        return path.read_text(encoding="utf-8")
    return BytesIO(path.read_bytes())


@pytest.mark.parametrize(
    ("path", "kind"),
    [
        (SAMPLES / "valid.xml", "path"),
        (SAMPLES / "valid.xml", "path_str"),
        (SAMPLES / "valid.xml", "text"),
        (SAMPLES / "valid.xml", "bytes"),
        (SAMPLES / "valid_bom.xml", "path"),
        (SAMPLES / "valid_bom.xml", "text"),
        (SAMPLES / "valid_bom.xml", "bytes"),
        (DATA_SAMPLE, "path"),
        (SAMPLES / "large_csv_2.csv", "path"),
        (SAMPLES / "bis_der.json", "text"),
    ],
)
def test_stream_sdmx_same_text_as_process_string_to_read(path, kind):
    chunks, read_format = stream_sdmx(_source(path, kind))
    expected = process_string_to_read(_source(path, kind))
    assert ("".join(chunks), read_format) == expected


@pytest.mark.parametrize("kind", ["path", "bytes"])
def test_stream_sdmx_small_chunks(monkeypatch, tmp_path, kind):
    text = DATA_SAMPLE.read_text(encoding="utf-8")
    text = "\ufeff" + text.replace("</", "\ufeff</", 1).replace("\n", "\r\n")
    path = tmp_path / "message.xml"
    path.write_bytes((text + "<!-- Pac\u00edfico -->").encode("utf-8"))
    with open(path, encoding="utf-8-sig", errors="replace") as f:
        expected = f.read().replace("\ufeff", "")
    monkeypatch.setattr(input_processor, "READ_CHUNK_CHARS", 7)

    chunks, read_format = stream_sdmx(_source(path, kind))

    head = next(chunks)
    assert len(head) >= 1000
    assert head + "".join(chunks) == expected
    assert read_format == Format.DATA_SDMX_ML_2_1_STR


def test_stream_sdmx_short_document():
    text = (
        '<?xml version="1.0"?><mes:Structure xmlns:mes="http://www.sdmx.org'
        '/resources/sdmxml/schemas/v2_1/message"/>'
    )
    chunks, read_format = stream_sdmx(text)
    assert list(chunks) == [text]
    assert read_format == Format.STRUCTURE_SDMX_ML_2_1


def test_stream_sdmx_invalid_input_closes_the_source():
    with pytest.raises(Invalid, match="Cannot parse input as SDMX-ML."):
        stream_sdmx("<?xmlAAAA")


def test_stream_sdmx_url_streams(respx_mock):
    body = (
        DATA_SAMPLE.read_text(encoding="utf-8") + "<!-- Pac\u00edfico -->"
    ).encode("utf-8")
    middle = body.index("\u00ed".encode()) + 1
    stream = ByteChunks([body[:middle], body[middle:]])
    respx_mock.get(URL).mock(return_value=httpx.Response(200, stream=stream))

    chunks, read_format = stream_sdmx(URL)

    assert "".join(chunks) == body.decode("utf-8")
    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    assert stream.closed


def test_stream_sdmx_url_error_with_xml_body(respx_mock):
    body = (SAMPLES / "error.xml").read_text(encoding="utf-8")
    respx_mock.get(URL).mock(return_value=httpx.Response(404, content=body))

    chunks, read_format = stream_sdmx(URL)

    assert "".join(chunks) == body
    assert read_format == Format.ERROR_SDMX_ML_2_1


def test_stream_sdmx_url_error_without_xml(respx_mock):
    respx_mock.get(URL).mock(return_value=httpx.Response(404, content=""))
    with pytest.raises(
        Invalid, match="Cannot retrieve a SDMX Message from URL"
    ):
        stream_sdmx(URL)


def test_stream_sdmx_url_fails_mid_stream(respx_mock):
    body = DATA_SAMPLE.read_bytes()
    stream = ByteChunks([body[:2000]], fail=True)
    respx_mock.get(URL).mock(return_value=httpx.Response(200, stream=stream))

    chunks, read_format = stream_sdmx(URL)

    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    with pytest.raises(
        Invalid, match="Cannot retrieve a SDMX Message from URL"
    ):
        list(chunks)
    assert stream.closed


def test_stream_sdmx_closes_url_stream(respx_mock):
    body = DATA_SAMPLE.read_bytes()
    stream = ByteChunks([body[:1500], body[1500:3000], body[3000:]])
    respx_mock.get(URL).mock(return_value=httpx.Response(200, stream=stream))

    chunks, _ = stream_sdmx(URL)
    assert next(chunks) == body[:1500].decode("utf-8")
    assert stream.yielded < 3
    assert not stream.closed

    chunks.close()

    assert stream.closed


@pytest.mark.parametrize("kind", ["path", "bytes"])
def test_stream_sdmx_csv_small_chunks(monkeypatch, tmp_path, kind):
    text = CSV_SAMPLE.read_text(encoding="utf-8").replace("\n", "\r\n")
    path = tmp_path / "data.csv"
    path.write_bytes(("\ufeff" + text).encode("utf-8"))
    expected = process_string_to_read(_source(path, kind))
    monkeypatch.setattr(input_processor, "READ_CHUNK_CHARS", 7)

    chunks, read_format = stream_sdmx(_source(path, kind))

    head = next(chunks)
    assert 1000 <= len(head) < len(expected[0])
    assert (head + "".join(chunks), read_format) == expected
    assert read_format == Format.DATA_SDMX_CSV_1_0_0


@pytest.mark.parametrize("size", [1, 10, 1000])
def test_stream_sdmx_csv_header_with_line_breaks(monkeypatch, size):
    # The first 1000 characters end with a line break within a quoted
    # header, so the header goes on in the next chunks
    head = 'KEY,"' + "A" * 10 + "\n" + "B" * 983 + "\n"
    text = head + 'C",DATAFLOW,X\nK,V,BIS:DF(1.0),1\n'
    assert len(head) == 1000
    monkeypatch.setattr(input_processor, "READ_CHUNK_CHARS", size)

    chunks, read_format = stream_sdmx(BytesIO(text.encode("utf-8")))

    assert "".join(chunks) == text
    assert read_format == Format.DATA_SDMX_CSV_1_0_0
    assert process_string_to_read(text) == (text, read_format)


def test_stream_sdmx_one_line_csv(monkeypatch):
    text = "DATAFLOW,DIM_1,OBS_VALUE"
    monkeypatch.setattr(input_processor, "READ_CHUNK_CHARS", 7)

    chunks, read_format = stream_sdmx(BytesIO(text.encode("utf-8")))

    assert "".join(chunks) == text
    assert read_format == Format.DATA_SDMX_CSV_1_0_0
    assert process_string_to_read(text) == (text, read_format)


@pytest.fixture
def csv_samples(monkeypatch):
    """The texts the SDMX-CSV check is given."""
    samples = []
    check_csv = input_processor.__check_csv

    def spy(sample):
        samples.append(sample)
        return check_csv(sample)

    monkeypatch.setattr(input_processor, "__check_csv", spy)
    return samples


def test_stream_sdmx_csv_checks_the_first_lines_only(csv_samples):
    # A str is a single chunk, which the checks do not read whole
    text = CSV_SAMPLE.read_text(encoding="utf-8")
    second_line_end = text.index("\n", text.index("\n") + 1) + 1
    assert second_line_end > 100

    chunks, read_format = stream_sdmx(text)

    assert csv_samples == [text[:second_line_end]]
    assert read_format == Format.DATA_SDMX_CSV_1_0_0
    assert "".join(chunks) == text


def test_stream_sdmx_csv_checks_100_characters_at_least(csv_samples):
    text = "DATAFLOW,DIM_1,OBS_VALUE\n" + "BIS:DF(1.0),A,1\n" * 100

    chunks, read_format = stream_sdmx(text)

    assert csv_samples == [text[:100]]
    assert read_format == Format.DATA_SDMX_CSV_1_0_0
    assert "".join(chunks) == text


def test_stream_sdmx_csv_error_in_header():
    # The csv module rejects a carriage return within an unquoted value
    text = "DATAFLOW,A,B\rC\n1,2,3\n4,5,6\n"
    with pytest.raises(csv.Error):
        process_string_to_read(text)
    with pytest.raises(csv.Error):
        stream_sdmx(text)


def test_stream_sdmx_csv_url_streams(respx_mock):
    body = CSV_SAMPLE.read_bytes()
    stream = ByteChunks([body[:1500], body[1500:3000], body[3000:]])
    respx_mock.get(URL).mock(return_value=httpx.Response(200, stream=stream))

    chunks, read_format = stream_sdmx(URL)

    assert read_format == Format.DATA_SDMX_CSV_1_0_0
    assert stream.yielded < 3
    assert "".join(chunks) == body.decode("utf-8")
    assert stream.closed


def _compressed_source(body, kind, tmp_path, respx_mock):
    """A gzip-compressed body as a file, a BytesIO or a URL."""
    if kind == "url":
        # The magic number is split across the first two chunks
        stream = ByteChunks([body[:1], *split(body[1:], 500)])
        respx_mock.get(URL).mock(
            return_value=httpx.Response(200, stream=stream)
        )
        return URL
    if kind == "bytes":
        return BytesIO(body)
    path = tmp_path / "message.gz"
    path.write_bytes(body)
    return path if kind == "path" else str(path)


@pytest.mark.parametrize("kind", ["path", "path_str", "bytes", "url"])
@pytest.mark.parametrize(
    ("sample", "expected_format"),
    [
        (DATA_SAMPLE, Format.DATA_SDMX_ML_2_1_STR),
        (CSV_SAMPLE, Format.DATA_SDMX_CSV_1_0_0),
    ],
)
def test_stream_sdmx_gzip(sample, expected_format, kind, tmp_path, respx_mock):
    text = sample.read_text(encoding="utf-8")
    body = gzip.compress(("\ufeff" + text).encode("utf-8"))

    chunks, read_format = stream_sdmx(
        _compressed_source(body, kind, tmp_path, respx_mock)
    )

    assert ("".join(chunks), read_format) == (text, expected_format)


@pytest.mark.parametrize("kind", ["path", "bytes", "url"])
def test_process_string_to_read_gzip(kind, tmp_path, respx_mock):
    text = CSV_SAMPLE.read_text(encoding="utf-8")
    body = gzip.compress(text.encode("utf-8"))

    result = process_string_to_read(
        _compressed_source(body, kind, tmp_path, respx_mock)
    )

    assert result == (text, Format.DATA_SDMX_CSV_1_0_0)


@pytest.mark.parametrize("kind", ["path", "bytes", "url"])
def test_stream_sdmx_gzip_members(kind, tmp_path, respx_mock):
    # A gzip stream may hold several members, one after the other
    text = CSV_SAMPLE.read_text(encoding="utf-8")
    middle = len(text) // 2
    body = gzip.compress(text[:middle].encode("utf-8")) + gzip.compress(
        text[middle:].encode("utf-8")
    )

    chunks, _ = stream_sdmx(
        _compressed_source(body, kind, tmp_path, respx_mock)
    )

    assert "".join(chunks) == text


@pytest.mark.parametrize(
    ("kind", "error"),
    [("path", EOFError), ("bytes", EOFError), ("url", Invalid)],
)
def test_stream_sdmx_truncated_gzip(kind, error, tmp_path, respx_mock):
    text = CSV_SAMPLE.read_text(encoding="utf-8")
    body = gzip.compress(text.encode("utf-8"))[:-10]
    source = _compressed_source(body, kind, tmp_path, respx_mock)

    with pytest.raises(error, match="end-of-stream marker"):
        "".join(stream_sdmx(source)[0])


def test_stream_sdmx_gzip_url_streams(respx_mock):
    text = DATA_SAMPLE.read_text(encoding="utf-8")
    body = gzip.compress(text.encode("utf-8"))
    parts = [body[:1], *split(body[1:], 500)]
    stream = ByteChunks(parts)
    respx_mock.get(URL).mock(return_value=httpx.Response(200, stream=stream))

    chunks, read_format = stream_sdmx(URL)

    assert read_format == Format.DATA_SDMX_ML_2_1_STR
    assert stream.yielded < len(parts)
    assert "".join(chunks) == text
    assert stream.closed


def test_stream_sdmx_gzip_url_with_content_encoding(respx_mock):
    # httpx decodes the Content-Encoding, then the gzip body it held is
    # decompressed
    text = CSV_SAMPLE.read_text(encoding="utf-8")
    body = gzip.compress(gzip.compress(text.encode("utf-8")))
    respx_mock.get(URL).mock(
        return_value=httpx.Response(
            200, content=body, headers={"Content-Encoding": "gzip"}
        )
    )

    chunks, read_format = stream_sdmx(URL)

    assert ("".join(chunks), read_format) == (
        text,
        Format.DATA_SDMX_CSV_1_0_0,
    )


def test_read_sdmx_gzip(tmp_path):
    path = tmp_path / "data.csv.gz"
    path.write_bytes(
        gzip.compress(CSV_SAMPLE.read_text(encoding="utf-8").encode("utf-8"))
    )

    message = read_sdmx(path)

    expected = read_sdmx(CSV_SAMPLE)
    assert message.data[0].short_urn == expected.data[0].short_urn
    pd.testing.assert_frame_equal(message.data[0].data, expected.data[0].data)


def test_stream_sdmx_url_empty_body(respx_mock):
    # The body is shorter than the gzip magic number, so it is read as text
    respx_mock.get(URL).mock(return_value=httpx.Response(200, content=b""))

    with pytest.raises(Invalid, match="Cannot parse input as SDMX."):
        stream_sdmx(URL)
