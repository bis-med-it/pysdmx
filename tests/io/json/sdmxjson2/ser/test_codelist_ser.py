from datetime import datetime, timedelta
from datetime import timezone as tz

import msgspec
import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonCodelist
from pysdmx.model import Agency, Annotation, Code, Codelist


@pytest.fixture
def codelist():
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
    )


@pytest.fixture
def codelist_org():
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
    )


@pytest.fixture
def codelist_no_name():
    return Codelist("CL_FREQ", agency="BIS")


def test_codelist(codelist: Codelist):
    sjson = JsonCodelist.from_model(codelist)

    assert sjson.id == codelist.id
    assert sjson.name == codelist.name
    assert sjson.agency == codelist.agency
    assert sjson.description == codelist.description
    assert sjson.version == codelist.version
    assert len(sjson.codes) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == codelist.valid_from
    assert sjson.validTo == codelist.valid_to


def test_codelist_org(codelist_org: Codelist):
    sjson = JsonCodelist.from_model(codelist_org)

    assert sjson.id == codelist_org.id
    assert sjson.name == codelist_org.name
    assert sjson.agency == codelist_org.agency.id
    assert sjson.description == codelist_org.description
    assert sjson.version == codelist_org.version
    assert len(sjson.codes) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == codelist_org.valid_from
    assert sjson.validTo == codelist_org.valid_to


def test_codelist_no_name(codelist_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonCodelist.from_model(codelist_no_name)


def test_codelist_validity_without_timezone_is_assumed_utc():
    cl = Codelist(
        "CL",
        name="CL",
        agency="BIS",
        valid_from=datetime(2020, 1, 1),
        valid_to=datetime(2030, 1, 1),
    )

    encoded = msgspec.json.encode(JsonCodelist.from_model(cl))

    assert b'"validFrom":"2020-01-01T00:00:00Z"' in encoded
    assert b'"validTo":"2030-01-01T00:00:00Z"' in encoded


def test_codelist_validity_keeps_its_timezone():
    cet = tz(timedelta(hours=1))
    cl = Codelist(
        "CL",
        name="CL",
        agency="BIS",
        valid_from=datetime(2020, 1, 1, tzinfo=cet),
    )

    encoded = msgspec.json.encode(JsonCodelist.from_model(cl))

    assert b'"validFrom":"2020-01-01T00:00:00+01:00"' in encoded
