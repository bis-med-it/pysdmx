from datetime import datetime

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.structure import (
    JsonStructureMessage,
    JsonStructures,
)
from pysdmx.model import Agency, AgencyScheme, Codelist, Organisation
from pysdmx.model.code import Code
from pysdmx.model.message import Header, StructureMessage


@pytest.fixture
def header():
    return Header(id="test42", test=True, sender=Organisation("BIS"))


@pytest.fixture
def codelist():
    code1 = Code("A", name="Code A")
    code2 = Code("B", name="Code B")
    return Codelist(
        id="CL_FREQ",
        name="Frequency Codelist",
        agency="BIS",
        version="1.0",
        items=[code1, code2],
    )


@pytest.fixture
def agency_scheme():
    agency = Agency("BIS", name="Bank for International Settlements")
    return AgencyScheme(agency="SDMX", items=[agency])


@pytest.fixture
def msg_with_structures(header, codelist, agency_scheme):
    return StructureMessage(header, [codelist, agency_scheme])


def test_structure_message(msg_with_structures: StructureMessage):
    sjson = JsonStructureMessage.from_model(msg_with_structures)

    # Check header
    assert sjson.meta is not None
    assert sjson.meta.id == "test42"
    assert sjson.meta.test is True
    assert sjson.meta.sender.id == "BIS"
    assert isinstance(sjson.meta.prepared, datetime)

    # Check structures
    assert sjson.data is not None
    assert isinstance(sjson.data, JsonStructures)
    assert len(sjson.data.codelists) == 1
    assert len(sjson.data.agencySchemes) == 1


def test_no_header(codelist):
    msg = StructureMessage(None, [codelist])

    with pytest.raises(errors.Invalid, match="messages must have a header"):
        JsonStructureMessage.from_model(msg)


def test_no_structures(header):
    msg = StructureMessage(header, [])

    with pytest.raises(
        errors.Invalid, match="structure messages must have structures"
    ):
        JsonStructureMessage.from_model(msg)
