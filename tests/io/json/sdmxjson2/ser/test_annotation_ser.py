import pytest

from pysdmx.io.json.sdmxjson2.messages.core import JsonAnnotation
from pysdmx.model import Annotation


@pytest.fixture
def annotation():
    return Annotation(
        id="test-id",
        title="Test Annotation",
        type="test-type",
        text="This is a test annotation.",
    )


@pytest.fixture
def annotation_with_url():
    return Annotation(
        id="test-id",
        title="Test Annotation",
        type="test-type",
        text="This is a test annotation.",
        url="http://test.org",
    )


def test_annotation(annotation: Annotation):
    sjson = JsonAnnotation.from_model(annotation)

    assert sjson.id == annotation.id
    assert sjson.title == annotation.title
    assert sjson.text == annotation.text
    assert len(sjson.links) == 0
    assert sjson.type == annotation.type


def test_annotation_with_href(annotation_with_url: Annotation):
    sjson = JsonAnnotation.from_model(annotation_with_url)

    assert sjson.id == annotation_with_url.id
    assert sjson.title == annotation_with_url.title
    assert sjson.text == annotation_with_url.text
    assert len(sjson.links) == 1
    lnk = sjson.links[0]
    assert lnk.href == annotation_with_url.url
    assert lnk.rel == "self"
    assert sjson.type == annotation_with_url.type
