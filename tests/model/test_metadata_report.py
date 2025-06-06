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


@pytest.fixture
def agency():
    return "BIS"


def test_full_initialization(
    id, name, structure, targets, attributes, version, agency
):
    report = MetadataReport(
        id=id,
        agency=agency,
        name=name,
        metadataflow=structure,
        targets=targets,
        attributes=attributes,
        version=version,
    )

    assert report.id == id
    assert report.name == name
    assert report.metadataflow == structure
    assert report.targets == targets
    assert report.attributes == attributes
    assert report.version == version
    assert report.agency == agency


def test_default_version(id, name, structure, targets, attributes, agency):
    report = MetadataReport(
        id=id,
        name=name,
        metadataflow=structure,
        targets=targets,
        attributes=attributes,
        agency=agency,
    )

    assert report.version == "1.0"


def test_immutable(id, name, structure, targets, attributes, agency):
    report = MetadataReport(
        id=id,
        name=name,
        metadataflow=structure,
        targets=targets,
        attributes=attributes,
        agency=agency,
    )
    with pytest.raises(AttributeError):
        report.name = "Update name"


def test_iterable(id, name, structure, targets, attributes, agency):
    report = MetadataReport(
        id=id,
        name=name,
        metadataflow=structure,
        targets=targets,
        attributes=attributes,
        agency=agency,
    )

    assert isinstance(report, Iterable)
    out = [attr.id for attr in report]
    assert len(out) == len(attributes)
    assert out == [a.id for a in attributes]


def test_sized(id, name, structure, targets, attributes, agency):
    report = MetadataReport(
        id=id,
        name=name,
        metadataflow=structure,
        targets=targets,
        attributes=attributes,
        agency=agency,
    )

    assert isinstance(report, Sized)
    assert len(report) == 4
    assert len(report.attributes) == 2


def test_get_attribute(id, name, structure, targets, attributes, agency):
    report = MetadataReport(
        id=id,
        name=name,
        metadataflow=structure,
        targets=targets,
        attributes=attributes,
        agency=agency,
    )

    resp1 = report["child2.child21.child211"]
    resp2 = report["child2"]
    resp3 = report["child3"]
    resp4 = report["child2.child24.child421"]

    assert resp1 == attributes[1].attributes[0].attributes[0]
    assert resp2 == attributes[1]
    assert resp3 is None
    assert resp4 is None


def test_serialization(id, name, structure, targets, attributes, agency):
    report = MetadataReport(
        id=id,
        name=name,
        metadataflow=structure,
        targets=targets,
        attributes=attributes,
        agency=agency,
    )

    ser = msgspec.msgpack.Encoder().encode(report)
    out = msgspec.msgpack.Decoder(MetadataReport).decode(ser)
    assert out == report


def test_tostr(id, name, structure, targets, attributes):
    report = MetadataReport(
        id, name, structure, targets, attributes, agency="BIS"
    )

    s = str(report)
    expected_str = ("id: id, "
                    "uri: name, "
                    "urn: urn:sdmx:org.sdmx.infomodel."
                    "metadatastructure.Metadataflow=BIS.MEDIT:DTI(1.0), "
                    "name: 1 strs, "
                    "description: 2 metadataattributes, "
                    "agency: BIS")

    assert s == expected_str


def test_tostr_empty(id, name, structure, targets):
    report = MetadataReport(id, name, structure, targets, [], agency="BIS")

    s = str(report)
    expected_str = ("id: id, "
                    "uri: name, "
                    "urn: urn:sdmx:org.sdmx.infomodel."
                    "metadatastructure.Metadataflow=BIS.MEDIT:DTI(1.0), "
                    "name: 1 strs, "
                    "agency: BIS")

    assert s == expected_str


def test_repr(id, name, structure, targets, attributes):
    report = MetadataReport(
        id, name, structure, targets, attributes, agency="BIS"
    )

    r = repr(report)
    expected_repr = ("MetadataReport("
                     "id='id', "
                     "uri='name', "
                     "urn='urn:sdmx:org.sdmx.infomodel."
                     "metadatastructure.Metadataflow=BIS.MEDIT:DTI(1.0)', "
                     "name=["
                     "'urn:sdmx:org.sdmx.infomodel.datastructure."
                     "Dataflow=BIS.CBS:CBS(1.0)'], "
                     "description=["
                     "MetadataAttribute("
                     "id='child1', "
                     "value='Child 1'), "
                     "MetadataAttribute("
                     "id='child2', "
                     "value='Child 2', "
                     "attributes=["
                     "MetadataAttribute("
                     "id='child21', "
                     "value='Child 2.1', "
                     "attributes=["
                     "MetadataAttribute("
                     "id='child211', "
                     "value='Child 2.1.1')])])], "
                     "agency='BIS')")

    assert r == expected_repr


def test_repr_empty(id, name, structure, targets):
    report = MetadataReport(id, name, structure, targets, [], agency="BIS")

    r = repr(report)
    expected_repr = ("MetadataReport("
                     "id='id', "
                     "uri='name', "
                     "urn='urn:sdmx:org.sdmx.infomodel."
                     "metadatastructure.Metadataflow=BIS.MEDIT:DTI(1.0)', "
                     "name=["
                     "'urn:sdmx:org.sdmx.infomodel.datastructure."
                     "Dataflow=BIS.CBS:CBS(1.0)'], "
                     "agency='BIS')")

    assert r == expected_repr
