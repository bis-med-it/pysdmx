from datetime import datetime, timezone as tz

import pytest

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
