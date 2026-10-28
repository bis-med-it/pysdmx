from io import BytesIO, StringIO
from pathlib import Path

import httpx
import msgspec
import pandas as pd
import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.csv.__csv_aux_reader import _TextChunks, read_csv_chunks
from pysdmx.io.csv.sdmx10 import reader as reader_10
from pysdmx.io.csv.sdmx20 import reader as reader_20
from pysdmx.io.csv.sdmx21 import reader as reader_21
from tests.io.byte_chunks import ByteChunks, split

TESTS = Path(__file__).parents[1]
CSV_SAMPLES = sorted(TESTS.rglob("*.csv"))
DATA_V1 = TESTS / "samples" / "data_v1.csv"
DATA_V2 = TESTS / "csv" / "sdmx20" / "reader" / "samples" / "data_v2.csv"
DATA_V21 = TESTS / "samples" / "large_csv_2.csv"
URL = "https://sdmx.example.org/data"


def _read_csv(text):
    return pd.read_csv(StringIO(text), keep_default_na=False, na_values=[])


def _assert_same_datasets(actual, expected):
    assert len(actual) == len(expected)
    for dataset, other in zip(actual, expected):
        fields = msgspec.structs.asdict(dataset)
        other_fields = msgspec.structs.asdict(other)
        pd.testing.assert_frame_equal(
            fields.pop("data"), other_fields.pop("data")
        )
        assert fields == other_fields


def test_text_chunks_reads_the_size_asked():
    stream = _TextChunks(iter(["ab", "", "cde", "f"]))

    assert stream.readable()
    assert stream.mode == "r"
    assert stream.read(3) == "abc"
    assert stream.read(1) == "d"
    assert stream.read(0) == ""
    assert stream.read(5) == "ef"
    assert stream.read(5) == ""


@pytest.mark.parametrize("size", [-1, None])
def test_text_chunks_reads_the_rest(size):
    stream = _TextChunks(["ab", "cd", "e"])

    assert stream.read(1) == "a"
    assert stream.read(size) == "bcde"
    assert stream.read(size) == ""


def test_text_chunks_reads_a_chunk_without_copying_it():
    text = "x" * 1000 + "y"
    stream = _TextChunks([text])

    assert stream.read(1000) == "x" * 1000
    assert stream._TextChunks__text is text
    assert stream.read() == "y"


@pytest.mark.parametrize(
    "path",
    CSV_SAMPLES,
    ids=lambda path: path.relative_to(TESTS).as_posix(),
)
def test_read_csv_chunks_same_as_reading_the_text(path):
    text = path.read_text(encoding="utf-8")
    expected = _read_csv(text)

    for size in (1, 7, 1000):
        pd.testing.assert_frame_equal(
            read_csv_chunks(split(text, size)), expected
        )


def test_read_csv_chunks_line_breaks_within_values():
    text = (
        "DATAFLOW,DIM_1,OBS_VALUE,COMMENT\r\n"
        'BIS:DF(1.0),"A\r\nB",1.50,"x, ""y""\nz"\r\n'
        "BIS:DF(1.0),C,2,\r\n"
    )
    expected = _read_csv(text)
    assert len(expected) == 2

    for size in (1, 2, 3):
        pd.testing.assert_frame_equal(
            read_csv_chunks(split(text, size)), expected
        )


@pytest.mark.parametrize(
    ("reader", "path"),
    [(reader_10, DATA_V1), (reader_20, DATA_V2), (reader_21, DATA_V21)],
)
def test_read_stream_same_as_read(reader, path):
    text = path.read_text(encoding="utf-8")

    datasets = reader.read_stream(split(text, 7))

    _assert_same_datasets(datasets, reader.read(text))


def _source(path, kind):
    if kind == "path":
        return path
    if kind == "path_str":
        return str(path)
    if kind == "text":
        return path.read_text(encoding="utf-8")
    return BytesIO(path.read_bytes())


@pytest.mark.parametrize("kind", ["path", "path_str", "text", "bytes"])
@pytest.mark.parametrize(
    ("reader", "path"), [(reader_10, DATA_V1), (reader_21, DATA_V21)]
)
def test_read_sdmx_csv(reader, path, kind):
    message = read_sdmx(_source(path, kind))

    assert message.header is None
    _assert_same_datasets(
        message.data, reader.read(path.read_text(encoding="utf-8"))
    )


def test_read_sdmx_csv_from_url(respx_mock):
    body = DATA_V1.read_bytes()
    stream = ByteChunks(split(body, 1000))
    respx_mock.get(URL).mock(return_value=httpx.Response(200, stream=stream))

    message = read_sdmx(URL)

    _assert_same_datasets(message.data, reader_10.read(body.decode("utf-8")))
    assert stream.closed


def test_read_sdmx_invalid_csv_closes_the_url_stream(respx_mock):
    # From the text, whose line breaks do not depend on the checkout
    text = DATA_V1.read_text(encoding="utf-8").encode("utf-8")
    header, rows = text.split(b"\n", 1)
    lines = rows.split(b"\n")
    lines[9] += b",X"
    body = header + b"\n" + b"\n".join(lines) + rows * 4
    chunks = split(body, 1000)
    stream = ByteChunks(chunks)
    respx_mock.get(URL).mock(return_value=httpx.Response(200, stream=stream))

    with pytest.raises(pd.errors.ParserError, match="line 11"):
        read_sdmx(URL)

    assert stream.yielded < len(chunks)
    assert stream.closed
