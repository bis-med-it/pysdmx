from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonHierarchy
from pysdmx.model import (
    Agency,
    Annotation,
    HierarchicalCode,
    Hierarchy,
    LevelType,
)


@pytest.fixture
def hierarchy():
    hc = HierarchicalCode(
        "A",
        urn="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:Z(1.0).V",
    )
    return Hierarchy(
        "H1",
        name="Hierarchy 1",
        agency="BIS",
        description="Just a test hierarchy",
        version="1.1",
        codes=[hc],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
    )


@pytest.fixture
def hierarchy_org():
    hc = HierarchicalCode(
        "A",
        urn="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:Z(1.0).V",
    )
    return Hierarchy(
        "H1",
        name="Hierarchy 1",
        agency=Agency("BIS"),
        description="Just a test hierarchy",
        version="1.1",
        codes=[hc],
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        is_partial=True,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
    )


@pytest.fixture
def hierarchy_no_name():
    return Hierarchy("CL_FREQ", agency="BIS")


@pytest.fixture
def hierarchy_with_levels():
    hc = HierarchicalCode(
        "A",
        urn="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:Z(1.0).V",
        level="1",
    )
    return Hierarchy(
        "H1",
        name="Hierarchy 1",
        agency="BIS",
        version="1.1",
        codes=[hc],
        has_formal_levels=True,
        level=LevelType(
            id="0",
            name="Division",
            level=LevelType(id="1", name="Group"),
        ),
    )


@pytest.fixture
def hierarchy_with_level_no_name():
    hc = HierarchicalCode(
        "A",
        urn="urn:sdmx:org.sdmx.infomodel.codelist.Codelist=TEST:Z(1.0).V",
        level="1",
    )
    return Hierarchy(
        "H1",
        name="Hierarchy 1",
        agency="BIS",
        version="1.1",
        codes=[hc],
        has_formal_levels=True,
        level=LevelType(id="0", name="Division", level=LevelType(id="1")),
    )


def test_hierarchy(hierarchy: Hierarchy):
    sjson = JsonHierarchy.from_model(hierarchy)

    assert sjson.id == hierarchy.id
    assert sjson.name == hierarchy.name
    assert sjson.agency == hierarchy.agency
    assert sjson.description == hierarchy.description
    assert sjson.version == hierarchy.version
    assert len(sjson.hierarchicalCodes) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == hierarchy.valid_from
    assert sjson.validTo == hierarchy.valid_to


def test_hierarchy_org(hierarchy_org: Hierarchy):
    sjson = JsonHierarchy.from_model(hierarchy_org)

    assert sjson.id == hierarchy_org.id
    assert sjson.name == hierarchy_org.name
    assert sjson.agency == hierarchy_org.agency.id
    assert sjson.description == hierarchy_org.description
    assert sjson.version == hierarchy_org.version
    assert len(sjson.hierarchicalCodes) == 1
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.isPartial is True
    assert sjson.validFrom == hierarchy_org.valid_from
    assert sjson.validTo == hierarchy_org.valid_to


def test_hierarchy_no_name(hierarchy_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonHierarchy.from_model(hierarchy_no_name)


def test_hierarchy_with_levels(hierarchy_with_levels: Hierarchy):
    sjson = JsonHierarchy.from_model(hierarchy_with_levels)

    assert sjson.hasFormalLevels is True
    assert sjson.level is not None
    assert sjson.level.id == "0"
    assert sjson.level.name == "Division"
    assert sjson.level.level is not None
    assert sjson.level.level.id == "1"
    assert sjson.level.level.name == "Group"
    assert sjson.level.level.level is None
    assert sjson.hierarchicalCodes[0].level == "1"


def test_hierarchy_with_level_no_name(
    hierarchy_with_level_no_name: Hierarchy,
):
    with pytest.raises(
        errors.Invalid, match="hierarchy levels must have a name"
    ):
        JsonHierarchy.from_model(hierarchy_with_level_no_name)
