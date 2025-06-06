from typing import Iterable, Sized

import msgspec
import pytest

from pysdmx.model import MetadataAttribute, MetadataReport


@pytest.fixture
def id():
    return "id"


@pytest.fixture
def name():
    return "name"


@pytest.fixture
def structure():
    return (
        "urn:sdmx:org.sdmx.infomodel.metadatastructure.Metadataflow="
        "BIS.MEDIT:DTI(1.0)"
    )


@pytest.fixture
def targets():
    return [
        "urn:sdmx:org.sdmx.infomodel.datastructure.Dataflow=BIS.CBS:CBS(1.0)",
    ]


@pytest.fixture
def attributes():
    grandchild = MetadataAttribute("child211", "Child 2.1.1")
    child = MetadataAttribute("child21", "Child 2.1", [grandchild])
    return [
        MetadataAttribute("child1", "Child 1"),
        MetadataAttribute("child2", "Child 2", [child]),
    ]


@pytest.fixture
def version():
    return "1.0.42"


def test_full_initialization(
    id, name, structure, targets, attributes, version
):
    report = MetadataReport(id, name, structure, targets, attributes, version)

    assert report.id == id
    assert report.name == name
    assert report.metadataflow == structure
    assert report.targets == targets
    assert report.attributes == attributes
    assert report.version == version


def test_default_version(id, name, structure, targets, attributes):
    report = MetadataReport(id, name, structure, targets, attributes)

    assert report.id == id
    assert report.name == name
    assert report.metadataflow == structure
    assert report.targets == targets
    assert report.attributes == attributes
    assert report.version == "1.0"


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


def test_sized(id, name, structure, targets, attributes):
    report = MetadataReport(id, name, structure, targets, attributes)

    assert isinstance(report, Sized)
    assert len(report) == 4
    assert len(report.attributes) == 2


def test_get_attribute(id, name, structure, targets, attributes):
    report = MetadataReport(id, name, structure, targets, attributes)

    resp1 = report["child2.child21.child211"]
    resp2 = report["child2"]
    resp3 = report["child3"]
    resp4 = report["child2.child24.child421"]

    assert resp1 == attributes[1].attributes[0].attributes[0]
    assert resp2 == attributes[1]
    assert resp3 is None
    assert resp4 is None


def test_serialization(id, name, structure, targets, attributes):
    rep = MetadataReport(id, name, structure, targets, attributes)

    ser = msgspec.msgpack.Encoder().encode(rep)
    out = msgspec.msgpack.Decoder(MetadataReport).decode(ser)
    assert out == rep


def test_tostr(id, name, structure, targets, attributes):
    report = MetadataReport(id, name, structure, targets, attributes)

    s = str(report)
    expected_str = (
        f"id: {id}, name: {name}, metadataflow: {structure}, "
        f"targets: 1 strs, attributes: 2 metadataattributes, version: 1.0"
    )

    assert s == expected_str


def test_tostr_empty(id, name, structure, targets):
    report = MetadataReport(id, name, structure, targets, [])

    s = str(report)
    expected_str = (
        f"id: {id}, name: {name}, metadataflow: {structure}, "
        f"targets: 1 strs, version: 1.0"
    )

    assert s == expected_str


def test_repr(id, name, structure, targets, attributes):
    report = MetadataReport(id, name, structure, targets, attributes)

    r = repr(report)
    expected_repr = (
        f"MetadataReport(id={id!r}, name={name!r}, "
        f"metadataflow={structure!r}, targets={targets!r}, "
        f"attributes={attributes!r}, version='1.0')"
    )

    assert r == expected_repr


def test_repr_empty(id, name, structure, targets):
    report = MetadataReport(id, name, structure, targets, [])

    r = repr(report)
    expected_repr = (
        f"MetadataReport(id={id!r}, name={name!r}, "
        f"metadataflow={structure!r}, targets={targets!r}, "
        f"version='1.0')"
    )

    assert r == expected_repr
