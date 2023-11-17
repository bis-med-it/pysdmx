from typing import Iterable, Sized

import pytest

from pysdmx.model import MetadataAttribute, MetadataReport


@pytest.fixture()
def id():
    return "id"


@pytest.fixture()
def name():
    return "name"


@pytest.fixture()
def structure():
    return (
        "urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow="
        "BIS.MEDIT:DTI(1.0)"
    )


@pytest.fixture()
def targets():
    return [
        "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS.CBS:CBS(1.0)",
    ]


@pytest.fixture()
def attributes():
    return [
        MetadataAttribute("child1", 42),
        MetadataAttribute("child2", "*"),
    ]


def test_full_initialization(id, name, structure, targets, attributes):
    report = MetadataReport(id, name, structure, targets, attributes)

    assert report.id == id
    assert report.name == name
    assert report.metadataflow == structure
    assert report.targets == targets
    assert report.attributes == attributes


def test_immutable(id, name, structure, targets, attributes):
    report = MetadataReport(id, name, structure, targets, attributes)
    with pytest.raises(AttributeError):
        report.name = "Update name"


def test_iterable(id, name, structure, targets, attributes):
    report = MetadataReport(id, name, structure, targets, attributes)

    assert isinstance(report, Iterable)
    out = [attr.id for attr in report]
    assert len(out) == len(attributes)
    assert out == [a.id for a in attributes]


def test_sized(id, name, structure, targets):
    grandchild = MetadataAttribute("child211", "Child 2.1.1")
    child = MetadataAttribute("child21", "Child 2.1", [grandchild])
    attrs = [
        MetadataAttribute("child1", "Child 1"),
        MetadataAttribute("child2", "Child 2", [child]),
    ]
    report = MetadataReport(id, name, structure, targets, attrs)

    assert isinstance(report, Sized)
    assert len(report) == 4
    assert len(report.attributes) == 2


def test_get_attribute(id, name, structure, targets):
    grandchild = MetadataAttribute("child211", "Child 2.1.1")
    child = MetadataAttribute("child21", "Child 2.1", [grandchild])
    attrs = [
        MetadataAttribute("child1", "Child 1"),
        MetadataAttribute("child2", "Child 2", [child]),
    ]

    report = MetadataReport(id, name, structure, targets, attrs)

    resp1 = report["child2.child21.child211"]
    resp2 = report["child2"]
    resp3 = report["child3"]
    resp4 = report["child2.child24.child421"]

    assert resp1 == grandchild
    assert resp2 == attrs[1]
    assert resp3 is None
    assert resp4 is None
