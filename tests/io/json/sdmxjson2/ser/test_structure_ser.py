import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.structure import JsonStructureMessage
from pysdmx.model import Agency, Code, Codelist
from pysdmx.model.message import Header, StructureMessage


@pytest.fixture
def message():
    a = Agency("BIS")
    cd = Code("A", name="Annual")
    cl = Codelist("CL_FREQ", agency=a, name="Frequency codelist", items=[cd])
    h = Header(sender=a)
    return StructureMessage(h, [cl])


@pytest.fixture
def message_no_header():
    a = Agency("BIS")
    cd = Code("A", name="Annual")
    cl = Codelist("CL_FREQ", agency=a, name="Frequency codelist", items=[cd])
    return StructureMessage(structures=[cl])


@pytest.fixture
def message_no_structures_1():
    a = Agency("BIS")
    h = Header(sender=a)
    return StructureMessage(h)


@pytest.fixture
def message_no_structures_2():
    a = Agency("BIS")
    h = Header(sender=a)
    return StructureMessage(h, [])


def test_message(message: StructureMessage):
    sjson = JsonStructureMessage.from_model(message)

    assert sjson.meta is not None
    assert len(sjson.data.codelists) == 1


def test_message_no_header(message_no_header: StructureMessage):
    with pytest.raises(errors.Invalid, match="must have a header"):
        JsonStructureMessage.from_model(message_no_header)


def test_message_no_structures_1(message_no_structures_1: StructureMessage):
    with pytest.raises(errors.Invalid, match="one maintainable artefact"):
        JsonStructureMessage.from_model(message_no_structures_1)


def test_message_no_structures_2(message_no_structures_2: StructureMessage):
    with pytest.raises(errors.Invalid, match="one maintainable artefact"):
        JsonStructureMessage.from_model(message_no_structures_2)
