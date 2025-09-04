import pytest

from pysdmx.io.json.sdmxjson2.messages.report import (
    JsonMetadataAttribute,
)
from pysdmx.model import Facets, MetadataAttribute


@pytest.fixture
def attr():
    child = MetadataAttribute("A1", value="Child A1")
    return MetadataAttribute(
        "A",
        value="Annual",
        attributes=[child],
        format=Facets(min_length=1, max_length=256),
    )


def test_attr(attr: MetadataAttribute):
    sjson = JsonMetadataAttribute.from_model(attr)

    assert sjson.id == attr.id
    assert sjson.value == attr.value
    assert len(sjson.annotations) == 0
    assert len(sjson.attributes) == 1
    assert sjson.attributes[0].id == "A1"
    assert sjson.attributes[0].format is None
    assert sjson.format.minLength == 1
    assert sjson.format.maxLength == 256
