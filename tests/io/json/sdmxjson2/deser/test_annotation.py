import msgspec
import pytest

from pysdmx.io.json.sdmxjson2.messages import JsonCodelistMessage
from pysdmx.model import Codelist


@pytest.fixture
def body():
    with open(
        "tests/io/json/sdmxjson2/deser/samples/annot/hier.json", "rb"
    ) as f:
        return f.read()


def test_annotation_with_url(body):
    exp = "https://test.org/code-validity"

    res = msgspec.json.Decoder(JsonCodelistMessage).decode(body)
    cl = res.to_model()

    assert isinstance(cl, Codelist)
    assert len(cl.annotations) == 1
    a = cl.annotations[0]
    assert a.url == exp
