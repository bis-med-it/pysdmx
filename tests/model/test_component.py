import pytest

from pysdmx.errors import Invalid
from pysdmx.model import (
    ArrayBoundaries,
    Code,
    Codelist,
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


@pytest.fixture()
def codes():
    c1 = Code("A", "Annual")
    c2 = Code("D", "Daily")
    return Codelist(
        "CL_FREQ", name="Frequency codelist", agency="BIS", items=[c1, c2]
    )


@pytest.fixture()
def facets():
    return Facets(min_length=2)


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
    assert not f.enumeration
    assert f.attachment_level is None


def test_full_initialization(
    fid, req, role, concept, typ, array_def, facets, codes
):
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
        codes,
        lvl,
        array_def,
    )

    assert f.id == fid
    assert f.required == req
    assert f.role == role
    assert f.concept == concept
    assert f.dtype == typ
    assert f.facets == facets
    assert f.name == name
    assert f.description == desc
    assert f.enumeration == codes
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
        f"(id={concept.id}, name={concept.name}), "
        "local_dtype=DataType.STRING"
    )


def test_dtype_property_local():
    concept = Concept("FREQ")

    component = Component(
        "FREQ", True, Role.DIMENSION, concept, DataType.ALPHA
    )

    assert component.concept.dtype is None
    assert component.local_dtype == DataType.ALPHA
    assert component.dtype == DataType.ALPHA


def test_dtype_property_core():
    concept = Concept("FREQ", dtype=DataType.ALPHA)

    component = Component("FREQ", True, Role.DIMENSION, concept)

    assert component.concept.dtype == DataType.ALPHA
    assert component.local_dtype is None
    assert component.dtype == DataType.ALPHA


def test_dtype_property_none():
    concept = Concept("FREQ")

    component = Component("FREQ", True, Role.DIMENSION, concept)

    assert component.concept.dtype is None
    assert component.local_dtype is None
    assert component.dtype == DataType.STRING


def test_facets_property_local(facets):
    concept = Concept("FREQ")

    component = Component(
        "FREQ", True, Role.DIMENSION, concept, local_facets=facets
    )

    assert component.concept.facets is None
    assert component.local_facets == facets
    assert component.facets == facets


def test_facets_property_core(facets):
    concept = Concept("FREQ", facets=facets)

    component = Component("FREQ", True, Role.DIMENSION, concept)

    assert component.concept.facets == facets
    assert component.local_facets is None
    assert component.facets == facets


def test_facets_property_none():
    concept = Concept("FREQ")

    component = Component("FREQ", True, Role.DIMENSION, concept)

    assert component.concept.facets is None
    assert component.local_facets is None
    assert component.facets is None


def test_codes_property_local(codes):
    concept = Concept("FREQ")

    component = Component(
        "FREQ", True, Role.DIMENSION, concept, local_codes=codes
    )

    assert component.concept.codes is None
    assert component.local_codes == codes
    assert component.enumeration == codes


def test_codes_property_core(codes):
    concept = Concept("FREQ", codes=codes)

    component = Component("FREQ", True, Role.DIMENSION, concept)

    assert component.concept.codes == codes
    assert component.local_codes is None
    assert component.enumeration == codes


def test_codes_property_none():
    concept = Concept("FREQ")

    component = Component("FREQ", True, Role.DIMENSION, concept)

    assert component.concept.codes is None
    assert component.local_codes is None
    assert component.enumeration is None


def test_invalid_role_attachment_level(concept):
    with pytest.raises(Invalid):
        Component(
            "FREQ",
            True,
            concept=concept,
            role=Role.DIMENSION,
            attachment_level="X",
        )

    with pytest.raises(Invalid):
        Component(
            "FREQ",
            True,
            concept=concept,
            role=Role.MEASURE,
            attribute_relationship={},
        )
