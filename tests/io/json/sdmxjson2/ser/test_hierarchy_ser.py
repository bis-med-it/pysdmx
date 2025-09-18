from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonHierarchy
from pysdmx.model import Agency, Annotation, HierarchicalCode, Hierarchy


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
