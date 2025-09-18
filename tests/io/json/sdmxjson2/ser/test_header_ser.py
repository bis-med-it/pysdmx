import pytest

from pysdmx.io.json.sdmxjson2.messages.core import JsonHeader
from pysdmx.model import Organisation
from pysdmx.model.message import Header


@pytest.fixture
def header():
    return Header(id="MYID", sender=Organisation("BIS"))


def test_header(header: Header):
    sjson = JsonHeader.from_model(header)

    assert sjson.id == header.id
    assert sjson.prepared == header.prepared
    assert sjson.sender == header.sender
    assert sjson.test is False
    assert len(sjson.contentLanguages) == 0
    assert sjson.name is None
    assert sjson.receivers is None
    assert len(sjson.links) == 0
