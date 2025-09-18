from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonValuelist
from pysdmx.model import Agency, Annotation, Code, Codelist


@pytest.fixture
def valuelist():
    c = Code("A", name="Annual")
    return Codelist(
        "CL_FREQ",
        name="Frequency",
        agency="BIS",
        description="FREQ cl",
        version="1.42",
        items=[c],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        sdmx_type="valuelist",
    )


@pytest.fixture
def valuelist_org():
    c = Code("A", name="Annual")
    return Codelist(
        "CL_FREQ",
        name="Frequency",
        agency=Agency("BIS"),
        description="FREQ cl",
        version="1.42",
        items=[c],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        sdmx_type="valuelist",
    )


@pytest.fixture
def valuelist_no_name():
    return Codelist("CL_FREQ", agency="BIS", sdmx_type="valuelist")


def test_valuelist(valuelist: Codelist):
    sjson = JsonValuelist.from_model(valuelist)

    assert sjson.id == valuelist.id
    assert sjson.name == valuelist.name
    assert sjson.agency == valuelist.agency
    assert sjson.description == valuelist.description
    assert sjson.version == valuelist.version
    assert len(sjson.valueItems) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == valuelist.valid_from
    assert sjson.validTo == valuelist.valid_to


def test_valuelist_org(valuelist_org: Codelist):
    sjson = JsonValuelist.from_model(valuelist_org)

    assert sjson.id == valuelist_org.id
    assert sjson.name == valuelist_org.name
    assert sjson.agency == valuelist_org.agency.id
    assert sjson.description == valuelist_org.description
    assert sjson.version == valuelist_org.version
    assert len(sjson.valueItems) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == valuelist_org.valid_from
    assert sjson.validTo == valuelist_org.valid_to


def test_valuelist_no_name(valuelist_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonValuelist.from_model(valuelist_no_name)
