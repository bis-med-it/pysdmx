from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.category import JsonCategoryScheme
from pysdmx.model import Agency, Annotation, Category, CategoryScheme


@pytest.fixture
def cs():
    c = Category("A", name="Annual")
    return CategoryScheme(
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
def cs_org():
    c = Category("A", name="Annual")
    return CategoryScheme(
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
def cs_no_name():
    return CategoryScheme("CL_FREQ", agency="BIS")


def test_cs(cs: CategoryScheme):
    sjson = JsonCategoryScheme.from_model(cs)

    assert sjson.id == cs.id
    assert sjson.name == cs.name
    assert sjson.agency == cs.agency
    assert sjson.description == cs.description
    assert sjson.version == cs.version
    assert len(sjson.categories) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == cs.valid_from
    assert sjson.validTo == cs.valid_to


def test_cs_org(cs_org: CategoryScheme):
    sjson = JsonCategoryScheme.from_model(cs_org)

    assert sjson.id == cs_org.id
    assert sjson.name == cs_org.name
    assert sjson.agency == cs_org.agency.id
    assert sjson.description == cs_org.description
    assert sjson.version == cs_org.version
    assert len(sjson.categories) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == cs_org.valid_from
    assert sjson.validTo == cs_org.valid_to


def test_cs_no_name(cs_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonCategoryScheme.from_model(cs_no_name)
