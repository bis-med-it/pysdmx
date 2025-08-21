from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.category import JsonCategorisation
from pysdmx.model import Agency, Annotation, Categorisation


@pytest.fixture
def cat():
    return Categorisation(
        "UUID",
        name="My categorisation",
        agency="BIS",
        description="My cat desc",
        version="1.42",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        source="BIS_MACRO",
        target="ID",
    )


@pytest.fixture
def cat_org():
    return Categorisation(
        "UUID",
        name="My categorisation",
        agency=Agency("BIS"),
        source="BIS_MACRO",
        target="ID",
    )


@pytest.fixture
def cat_no_name():
    return Categorisation(
        "UUID", agency=Agency("BIS"), source="BIS_MACRO", target="ID"
    )


def test_categorisation(cat: Categorisation):
    sjson = JsonCategorisation.from_model(cat)

    assert sjson.id == cat.id
    assert sjson.name == cat.name
    assert sjson.agency == cat.agency
    assert sjson.description == cat.description
    assert sjson.version == cat.version
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.validFrom == cat.valid_from
    assert sjson.validTo == cat.valid_to
    assert sjson.source == cat.source
    assert sjson.target == cat.target


def test_categorisation_org(cat_org: Categorisation):
    sjson = JsonCategorisation.from_model(cat_org)

    assert sjson.agency == cat_org.agency.id


def test_categorisation_no_name(cat_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonCategorisation.from_model(cat_no_name)
