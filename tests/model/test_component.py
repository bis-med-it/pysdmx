import pytest

from pysdmx.model import (
    ArrayBoundaries,
    Component,
    Concept,
    DataType,
    Facets,
    Role,
)


@pytest.fixture()
def fid():
    return "FREQ"


@pytest.fixture()
def req():
    return True


@pytest.fixture()
def role():
    return Role.DIMENSION


@pytest.fixture()
def typ():
    return DataType.STRING


@pytest.fixture()
def cl_ref():
    return "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_FREQ(1.0)"


@pytest.fixture()
def array_def():
    return ArrayBoundaries(1, 10)


@pytest.fixture()
def concept():
    return Concept("TEST", name="A test concept")


def test_defaults(fid, req, role, concept):
    f = Component(fid, req, role, concept)

    assert f.id == fid
    assert f.required == req
    assert f.role == role
    assert f.concept == concept
    assert f.dtype == DataType.STRING
    assert f.facets is None
    assert f.name is None
    assert f.description is None
    assert not f.codes
    assert f.attachment_level is None


def test_full_initialization(fid, req, role, concept, typ, array_def):
    facets = Facets(min_value=0, max_value="100")
    name = "Signal quality"
    desc = "The quality of the GPS signal"
    lvl = "O"

    f = Component(
        fid,
        req,
        role,
        concept,
        typ,
        facets,
        name,
        desc,
        attachment_level=lvl,
        array_def=array_def,
    )

    assert f.id == fid
    assert f.required == req
    assert f.role == role
    assert f.concept == concept
    assert f.dtype == typ
    assert f.facets == facets
    assert f.name == name
    assert f.description == desc
    assert not f.codes
    assert f.attachment_level == lvl
    assert f.array_def == array_def


def test_immutable(fid, req, role, concept, typ):
    f = Component(fid, req, role, concept, typ)
    with pytest.raises(AttributeError):
        f.name = fid


def test_equal(fid, req, role, concept, typ):
    f1 = Component(fid, req, role, concept, typ)
    f2 = Component(fid, req, role, concept, typ)

    assert f1 == f2


def test_not_equal(fid, req, role, concept, typ):
    f1 = Component(fid, req, role, concept, typ)
    f2 = Component(fid, req, role, concept, typ, name=fid)

    assert f1 != f2


def test_tostr(fid, req, role, concept, typ):
    f1 = Component(fid, req, role, concept, typ)

    s = str(f1)

    assert s == (
        f"id={fid}, required=True, role=Role.DIMENSION, concept="
        f"(id={concept.id}, name={concept.name}, dtype=DataType.STRING), "
        "dtype=DataType.STRING"
    )
