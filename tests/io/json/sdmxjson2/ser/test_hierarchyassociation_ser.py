from datetime import datetime
from datetime import timezone as tz

import pytest

from pysdmx import errors
from pysdmx.io.json.sdmxjson2.messages.code import JsonHierarchyAssociation
from pysdmx.model import Agency, Annotation, HierarchyAssociation


@pytest.fixture
def ha():
    return HierarchyAssociation(
        "UUID",
        name="My categorisation",
        agency="BIS",
        description="My cat desc",
        version="1.42",
        annotations=[Annotation(type="test")],
        is_external_reference=False,
        valid_from=datetime.now(tz.utc),
        valid_to=datetime.now(tz.utc),
        hierarchy="hierarchy_urn",
        component_ref="component_urn",
        context_ref="dataflow_urn",
    )


@pytest.fixture
def ha_org():
    return HierarchyAssociation(
        "UUID",
        name="My categorisation",
        agency=Agency("BIS"),
        hierarchy="hierarchy_urn",
        component_ref="component_urn",
        context_ref="dataflow_urn",
    )


@pytest.fixture
def ha_no_name():
    return HierarchyAssociation(
        "UUID",
        agency=Agency("BIS"),
        hierarchy="hierarchy_urn",
        component_ref="component_urn",
        context_ref="dataflow_urn",
    )


@pytest.fixture
def ha_no_hierarchy():
    return HierarchyAssociation(
        "UUID",
        name="My categorisation",
        agency=Agency("BIS"),
        component_ref="component_urn",
        context_ref="dataflow_urn",
    )


@pytest.fixture
def ha_no_component():
    return HierarchyAssociation(
        "UUID",
        name="My categorisation",
        agency=Agency("BIS"),
        hierarchy="hierarchy_urn",
        context_ref="dataflow_urn",
    )


@pytest.fixture
def ha_no_context():
    return HierarchyAssociation(
        "UUID",
        name="My categorisation",
        agency=Agency("BIS"),
        hierarchy="hierarchy_urn",
        component_ref="component_urn",
    )


def test_ha(ha: HierarchyAssociation):
    sjson = JsonHierarchyAssociation.from_model(ha)

    assert sjson.id == ha.id
    assert sjson.name == ha.name
    assert sjson.agency == ha.agency
    assert sjson.description == ha.description
    assert sjson.version == ha.version
    assert len(sjson.annotations) == 1
    assert sjson.isExternalReference is False
    assert sjson.validFrom == ha.valid_from
    assert sjson.validTo == ha.valid_to
    assert sjson.linkedHierarchy == ha.hierarchy
    assert sjson.contextObject == ha.context_ref
    assert sjson.linkedObject == ha.component_ref


def test_ha_org(ha_org: HierarchyAssociation):
    sjson = JsonHierarchyAssociation.from_model(ha_org)

    assert sjson.agency == ha_org.agency.id


def test_ha_no_name(ha_no_name):
    with pytest.raises(errors.Invalid, match="must have a name"):
        JsonHierarchyAssociation.from_model(ha_no_name)


def test_ha_no_hierarchy(ha_no_hierarchy):
    with pytest.raises(errors.Invalid, match="must reference a hierarchy"):
        JsonHierarchyAssociation.from_model(ha_no_hierarchy)


def test_ha_no_component(ha_no_component):
    with pytest.raises(errors.Invalid, match="must reference a component"):
        JsonHierarchyAssociation.from_model(ha_no_component)


def test_ha_no_context(ha_no_context):
    with pytest.raises(errors.Invalid, match="must reference a context"):
        JsonHierarchyAssociation.from_model(ha_no_context)
