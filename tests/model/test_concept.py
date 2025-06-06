import pytest

from pysdmx.model import Concept, DataType, Facets


@pytest.fixture
def fid():
    return "FREQ"


@pytest.fixture
def name():
    return "Frequency"


@pytest.fixture
def desc():
    return "The frequency of the data"


@pytest.fixture
def typ():
    return DataType.STRING


@pytest.fixture
def facets():
    return Facets(min_length=1, max_length=10)


def test_defaults(fid):
    f = Concept(id=fid)

    assert f.id == fid
    assert f.dtype is None
    assert f.facets is None
    assert f.name is None
    assert f.description is None
    assert not f.codes
    assert f.enum_ref is None


def test_full_initialization(fid):
    dtype = DataType.INTEGER
    facets = Facets(min_value=0, max_value=100)
    name = "Signal quality"
    desc = "The quality of the GPS signal"

    f = Concept(
        id=fid, dtype=dtype, facets=facets, name=name, description=desc
    )

    assert f.id == fid
    assert f.dtype == dtype
    assert f.facets == facets
    assert f.name == name
    assert f.description == desc
    assert not f.codes
    assert f.enum_ref is None


def test_immutable(fid, typ):
    f = Concept(id=fid, dtype=typ)
    with pytest.raises(AttributeError):
        f.name = fid


def test_equal(fid, typ):
    f1 = Concept(id=fid, dtype=typ)
    f2 = Concept(id=fid, dtype=typ)

    assert f1 == f2


def test_not_equal(fid, typ):
    f1 = Concept(id=fid, dtype=typ)
    f2 = Concept(id=fid, dtype=typ, name=fid)

    assert f1 != f2


def test_tostr_id(fid):
    c = Concept(id=fid)

    s = str(c)
    expected_str = f"id: {fid}"

    assert s == expected_str


def test_tostr_name(fid, name):
    c = Concept(id=fid, name=name)

    s = str(c)
    expected_str = f"id: {fid}, name: {name}"

    assert s == expected_str


def test_tostr_full(fid, name, desc, typ):
    c = Concept(id=fid, name=name, description=desc, dtype=typ)

    s = str(c)
    expected_str = (
        f"id: {fid}, name: {name}, description: {desc}, dtype: {typ}"
    )

    assert s == expected_str


def test_torepr_id(fid):
    c = Concept(id=fid)

    s = repr(c)
    expected_str = f"Concept(id={fid!r})"

    assert s == expected_str


def test_torepr_full(fid, name, desc, typ, facets):
    c = Concept(id=fid, name=name, description=desc, dtype=typ, facets=facets)

    s = repr(c)
    expected_str = f"Concept(id={fid!r}, name={name!r}, description={desc!r}, dtype={typ!r}, facets={facets!r})"

    assert s == expected_str
