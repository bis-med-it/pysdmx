from io import BytesIO
from pathlib import Path

import httpx
import msgspec
import pandas as pd
import pytest

from pysdmx.io import read_sdmx
from pysdmx.io.csv.sdmx10 import reader as reader_10
from pysdmx.io.csv.sdmx20 import reader as reader_20
from pysdmx.io.csv.sdmx21 import reader as reader_21
from tests.io.byte_chunks import ByteChunks, split

TESTS = Path(__file__).parents[1]
DATA_V1 = TESTS / "samples" / "data_v1.csv"
DATA_V2 = TESTS / "csv" / "sdmx20" / "reader" / "samples" / "data_v2.csv"
DATA_V21 = TESTS / "samples" / "large_csv_2.csv"
URL = "https://sdmx.example.org/data"


def _assert_same_datasets(actual, expected):
    assert len(actual) == len(expected)
    for dataset, other in zip(actual, expected):
        fields = msgspec.structs.asdict(dataset)
        other_fields = msgspec.structs.asdict(other)
        pd.testing.assert_frame_equal(
            fields.pop("data"), other_fields.pop("data")
        )
        assert fields == other_fields


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


def test_read_sdmx_large_csv_string():
    # A str is a single chunk, longer than two reads of pandas (256 Ki
    # characters each): the reads after the first one slice it
    header, rows = DATA_V1.read_text(encoding="utf-8").split("\n", 1)
    text = header + "\n" + rows * 8
    assert len(text) > 2 * 2**18

    message = read_sdmx(text)

    assert message.data[0].data.shape[0] == 8000
    _assert_same_datasets(message.data, reader_10.read_stream(split(text, 7)))


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
