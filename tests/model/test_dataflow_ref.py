import pytest

from pysdmx.model import DataflowRef


@pytest.fixture()
def dsi():
    return "ICP"


@pytest.fixture()
def name():
    return "ICP name"


@pytest.fixture()
def desc():
    return "ICP description"


@pytest.fixture()
def agency():
    return "5B0"


@pytest.fixture()
def version():
    return "1.0"


def test_basic_instantiation(dsi, agency):
    ds = DataflowRef(id=dsi, agency=agency)

    assert ds.id == dsi
    assert ds.name is None
    assert ds.description is None
    assert ds.agency == agency
    assert ds.version == "1.0"


def test_full_instantiation(dsi, name, desc, agency, version):
    ds = DataflowRef(
        id=dsi, agency=agency, name=name, description=desc, version=version
    )

    assert ds.id == dsi
    assert ds.name == name
    assert ds.description == desc
    assert ds.agency == agency
    assert ds.version == version


def test_immutable(dsi, agency):
    ds = DataflowRef(id=dsi, agency=agency)
    with pytest.raises(AttributeError):
        ds.name = "Not allowed"


def test_equal(dsi, name, desc, agency, version):
    ds1 = DataflowRef(
        id=dsi, agency=agency, name=name, description=desc, version=version
    )
    ds2 = DataflowRef(
        id=dsi, agency=agency, name=name, description=desc, version=version
    )

    assert ds1 == ds2


def test_not_equal(dsi, name, desc, agency, version):
    ds1 = DataflowRef(
        id=dsi, agency=agency, name=name, description=desc, version=version
    )
    ds2 = DataflowRef(
        id=dsi,
        agency=agency,
        name=name,
        description=desc,
        version=f"{version}.42",
    )

    assert ds1 != ds2


def test_tostr_id(dsi, agency):
    d = DataflowRef(id=dsi, agency=agency)

    s = str(d)

    assert s == f"id={dsi}, version={d.version}, agency={agency}"


def test_tostr_name(dsi, name, desc, agency, version):
    d = DataflowRef(
        id=dsi, agency=agency, name=name, description=desc, version=version
    )

    s = str(d)

    assert s == (
        f"id={dsi}, description={desc}, name={name}, "
        f"version={version}, agency={agency}"
    )
