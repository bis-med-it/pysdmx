import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonCodelistMessage
from pysdmx.model import Codelist


@pytest.fixture
def body_uri():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/annot/hier_uri.json", "rb"
    ) as f:
        return f.read()


@pytest.fixture
def body_href():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/annot/hier_href.json", "rb"
    ) as f:
        return f.read()


def test_annotation_with_uri(body_uri):
    exp = "https://test.org/code-validity"

    res = msgspec.json.Decoder(JsonCodelistMessage).decode(body_uri)
    cl = res.to_model()

    assert isinstance(cl, Codelist)
    assert len(cl.annotations) == 1
    a = cl.annotations[0]
    assert a.url == exp


def test_annotation_with_href(body_href):
    exp = "https://test.org/code-validity"

    res = msgspec.json.Decoder(JsonCodelistMessage).decode(body_href)
    cl = res.to_model()

    assert isinstance(cl, Codelist)
    assert len(cl.annotations) == 1
    a = cl.annotations[0]
    assert a.url == exp
