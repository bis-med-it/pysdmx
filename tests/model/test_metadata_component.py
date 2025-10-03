import pytest

from pysdmx.model import (
    ArrayBoundaries,
    Code,
    Codelist,
    Concept,
    DataType,
    Facets,
)
from pysdmx.model import (
    MetadataComponent as Component,
)


@pytest.fixture
def fid():
    return "FREQ"


@pytest.fixture
def typ():
    return DataType.STRING


@pytest.fixture
def cl_ref():
    return "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_FREQ(1.0)"


@pytest.fixture
def array_def():
    return ArrayBoundaries(1, 10)


@pytest.fixture
def concept():
    return Concept("TEST", name="A test concept")


@pytest.fixture
def codes():
    c1 = Code("A", "Annual")
    c2 = Code("D", "Daily")
    return Codelist(
        "CL_FREQ", name="Frequency codelist", agency="BIS", items=[c1, c2]
    )


@pytest.fixture
def facets():
    return Facets(min_length=2)


@pytest.fixture
def urn():
    return "urn:sdmx:org.sdmx.infomodel.codelist.Codelist=BIS:CL_FREQ(1.0)"


def test_defaults(fid, concept):
    f = Component(id=fid, concept=concept)

    assert f.id == fid
    assert f.is_presentational is False
    assert f.concept == concept
    assert f.dtype == DataType.STRING
    assert f.facets is None
    assert f.enumeration is None
    assert f.enum_ref is None
    assert len(f.components) == 0


def test_full_initialization(fid, concept, typ, array_def, facets, codes, urn):
    comps = Component(id="other", concept=Concept("other"))
    f = Component(
        id=fid,
        concept=concept,
        is_presentational=False,
        local_dtype=typ,
        local_facets=facets,
        local_codes=codes,
        array_def=array_def,
        local_enum_ref=urn,
        components=comps,
    )

    assert f.id == fid
    assert f.concept == concept
    assert f.is_presentational is False
    assert f.dtype == typ
    assert f.facets == facets
    assert f.enumeration == codes
    assert f.array_def == array_def
    assert f.enum_ref == urn
    assert f.components == comps


def test_immutable(fid, concept, typ):
    f = Component(id=fid, concept=concept, local_dtype=typ)
    with pytest.raises(AttributeError):
        f.is_presentational = True


def test_equal(fid, concept, typ):
    f1 = Component(id=fid, concept=concept, local_dtype=typ)
    f2 = Component(id=fid, concept=concept, local_dtype=typ)

    assert f1 == f2


def test_not_equal(fid, concept, typ):
    f1 = Component(id=fid, concept=concept, local_dtype=typ)
    f2 = Component(
        id=fid, concept=concept, local_dtype=typ, is_presentational=True
    )

    assert f1 != f2


def test_tostr(fid, concept, typ):
    f1 = Component(id=fid, concept=concept, local_dtype=typ)

    s = str(f1)
    expected_str = f"id: {fid}, concept: {concept}, local_dtype: String"

    assert s == expected_str


def test_dtype_property_local():
    concept = Concept("FREQ")

    component = Component(
        id="FREQ", concept=concept, local_dtype=DataType.ALPHA
    )

    assert component.concept.dtype is None
    assert component.local_dtype == DataType.ALPHA
    assert component.dtype == DataType.ALPHA


def test_dtype_property_core():
    concept = Concept("FREQ", dtype=DataType.ALPHA)

    component = Component(id="FREQ", concept=concept)

    assert component.concept.dtype == DataType.ALPHA
    assert component.local_dtype is None
    assert component.dtype == DataType.ALPHA


def test_dtype_property_none():
    concept = Concept("FREQ")

    component = Component(id="FREQ", concept=concept)

    assert component.concept.dtype is None
    assert component.local_dtype is None
    assert component.dtype == DataType.STRING


def test_facets_property_local(facets):
    concept = Concept("FREQ")

    component = Component(id="FREQ", concept=concept, local_facets=facets)

    assert component.concept.facets is None
    assert component.local_facets == facets
    assert component.facets == facets


def test_facets_property_core(facets):
    concept = Concept("FREQ", facets=facets)

    component = Component(id="FREQ", concept=concept)

    assert component.concept.facets == facets
    assert component.local_facets is None
    assert component.facets == facets


def test_facets_property_none():
    concept = Concept("FREQ")

    component = Component(id="FREQ", concept=concept)

    assert component.concept.facets is None
    assert component.local_facets is None
    assert component.facets is None


def test_codes_property_local(codes):
    concept = Concept("FREQ")

    component = Component(id="FREQ", concept=concept, local_codes=codes)

    assert component.concept.codes is None
    assert component.local_codes == codes
    assert component.enumeration == codes


def test_codes_property_core(codes):
    concept = Concept("FREQ", codes=codes)

    component = Component(id="FREQ", concept=concept)

    assert component.concept.codes == codes
    assert component.local_codes is None
    assert component.enumeration == codes


def test_codes_property_none():
    concept = Concept("FREQ")

    component = Component(id="FREQ", concept=concept)

    assert component.concept.codes is None
    assert component.local_codes is None
    assert component.enumeration is None


def test_core_enum_ref():
    i = Concept("FREQ", enum_ref="cl1")

    c = Component(id="FREQ", concept=i)

    assert c.local_enum_ref is None
    assert c.enum_ref == "cl1"


def test_local_enum_ref():
    i = Concept("FREQ")

    c = Component(id="FREQ", concept=i, local_enum_ref="cl1")

    assert c.local_enum_ref == "cl1"
    assert c.enum_ref == "cl1"


def test_no_enum_ref():
    i = Concept("FREQ")

    c = Component(id="FREQ", concept=i)

    assert c.local_enum_ref is None
    assert c.enum_ref is None


def test_torepr_full():
    child = Component(id="child", concept=Concept("child"))
    c = Component(
        id="top",
        concept=Concept("top"),
        components=[child],
    )

    s = repr(c)
    expected_str = (
        "MetadataComponent(id='top', concept=Concept(id='top'), "
        "components=[MetadataComponent(id='child', concept=Concept(id='child'))])"
    )

    assert s == expected_str
