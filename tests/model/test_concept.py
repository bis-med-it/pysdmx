import pytest

from pysdmx.model import Concept, DataType, Facets


@pytest.fixture()
def fid():
    return "FREQ"


@pytest.fixture()
def typ():
    return DataType.STRING


def test_defaults(fid):
    f = Concept(fid)

    assert f.id == fid
    assert f.dtype == DataType.STRING
    assert f.facets is None
    assert f.name is None
    assert f.description is None
    assert len(f.codes) == 0
    assert f.enum_ref is None


def test_full_initialization(fid):
    dtype = DataType.INTEGER
    facets = Facets(min_value=0, max_value="100")
    name = "Signal quality"
    desc = "The quality of the GPS signal"

    f = Concept(fid, dtype, facets, name, desc)

    assert f.id == fid
    assert f.dtype == dtype
    assert f.facets == facets
    assert f.name == name
    assert f.description == desc
    assert len(f.codes) == 0
    assert f.enum_ref is None


def test_immutable(fid, typ):
    f = Concept(fid, typ)
    with pytest.raises(AttributeError):
        f.name = fid


def test_equal(fid, typ):
    f1 = Concept(fid, typ)
    f2 = Concept(fid, typ)

    assert f1 == f2


def test_not_equal(fid, typ):
    f1 = Concept(fid, typ)
    f2 = Concept(fid, typ, name=fid)

    assert f1 != f2


def test_tostr(fid, typ):
    f1 = Concept(fid, typ)

    s = str(f1)

    assert s == f"id={fid}, dtype=String"
