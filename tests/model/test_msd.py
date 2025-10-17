from typing import Iterable, Sized

import msgspec
import pytest

from pysdmx.model.concept import Concept
from pysdmx.model.metadata import MetadataComponent, MetadataStructure


@pytest.fixture
def id():
    return "id"


@pytest.fixture
def name():
    return "name"


@pytest.fixture
def agency():
    return "5B0"


@pytest.fixture
def desc():
    return "description"


@pytest.fixture
def version():
    return "1.42.0"


@pytest.fixture
def components():
    grandchild = MetadataComponent(id="child211", concept=Concept("child211"))
    child = MetadataComponent(
        id="child21", concept=Concept("child21"), components=[grandchild]
    )
    return [
        MetadataComponent(id="child1", concept=Concept("child1")),
        MetadataComponent(
            id="child2", concept=Concept("child2"), components=[child]
        ),
    ]


def test_defaults(id, name, agency):
    msd = MetadataStructure(id=id, name=name, agency=agency)

    assert msd.id == id
    assert msd.name == name
    assert msd.agency == agency
    assert msd.description is None
    assert msd.version == "1.0"
    assert len(msd.components) == 0


def test_full_initialization(id, name, agency, desc, version, components):
    msd = MetadataStructure(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        components=components,
    )

    assert msd.id == id
    assert msd.name == name
    assert msd.agency == agency
    assert msd.description == desc
    assert msd.version == version
    assert msd.components == components
    assert len(msd) == 4
    assert len(msd.components) == 2


def test_immutable(id, name, agency):
    cs = MetadataStructure(id=id, name=name, agency=agency)
    with pytest.raises(AttributeError):
        cs.description = "Description"


def test_iterable(id, name, agency):
    comps = [
        MetadataComponent(id="child1", concept=Concept("child1")),
        MetadataComponent(id="child2", concept=Concept("child2")),
    ]
    cs = MetadataStructure(id=id, name=name, agency=agency, components=comps)

    assert isinstance(cs, Iterable)
    out = [c.id for c in cs]
    assert len(out) == 2
    assert out == ["child1", "child2"]


def test_sized(id, name, agency):
    cs = MetadataStructure(id=id, name=name, agency=agency)

    assert isinstance(cs, Sized)


def test_get_components(id, name, agency, components):
    cs = MetadataStructure(
        id=id, name=name, agency=agency, components=components
    )

    resp1 = cs["child2.child21.child211"]
    resp2 = cs["child2"]
    resp3 = cs["child3"]
    resp4 = cs["child2.child24.child421"]

    assert resp1 == components[1].components[0].components[0]
    assert "child2.child21.child211" in cs
    assert resp2 == components[1]
    assert "child2" in cs
    assert resp3 is None
    assert "child3" not in cs
    assert resp4 is None
    assert "child2.child24.child421" not in cs


def test_serialization(id, name, agency, desc, version, components):
    cs = MetadataStructure(
        id=id,
        name=name,
        agency=agency,
        description=desc,
        version=version,
        components=components,
    )

    ser = msgspec.msgpack.Encoder().encode(cs)

    out = msgspec.msgpack.Decoder(MetadataStructure).decode(ser)

    assert out == cs


@pytest.fixture
def msd(components):
    return MetadataStructure(
        id="STAT_SUBJECT_MATTER",
        name="SDMX Statistical Subject-Matter Domains",
        agency="SDMX",
        description="The SDMX Content Guidelines for "
        "Statistical Subject-Matter Domains",
        version="1.0",
        components=components,
    )


@pytest.fixture
def msd_no_items():
    return MetadataStructure(
        id="STAT_SUBJECT_MATTER",
        name="SDMX Statistical Subject-Matter Domains",
        agency="SDMX",
        description="The SDMX Content Guidelines for "
        "Statistical Subject-Matter Domains",
        version="1.0",
        components=[],
    )


def test_msd_str(msd):
    s = str(msd)
    expected_str = (
        "id: STAT_SUBJECT_MATTER, "
        "name: SDMX Statistical Subject-Matter Domains, "
        "description: The SDMX Content Guidelines "
        "for Statistical Subject-Matter Domains, "
        "version: 1.0, agency: SDMX, components: 2 components"
    )
    assert s == expected_str


def test_msd_no_items_str(msd_no_items):
    s = str(msd_no_items)
    expected_str = (
        "id: STAT_SUBJECT_MATTER, "
        "name: SDMX Statistical Subject-Matter Domains, "
        "description: The SDMX Content Guidelines "
        "for Statistical Subject-Matter Domains, "
        "version: 1.0, agency: SDMX"
    )
    assert s == expected_str
