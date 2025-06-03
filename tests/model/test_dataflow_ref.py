import pytest

from pysdmx.model import DataflowRef


@pytest.fixture
def dsi():
    return "ICP"


@pytest.fixture
def agency():
    return "5B0"


@pytest.fixture
def version():
    return "1.0"


def test_instantiation(dsi, agency):
    ds = DataflowRef(id=dsi, agency=agency)

    assert ds.id == dsi
    assert ds.agency == agency
    assert ds.version == "1.0"


def test_immutable(dsi, agency):
    ds = DataflowRef(id=dsi, agency=agency)
    with pytest.raises(AttributeError):
        ds.name = "Not allowed"


def test_equal(dsi, agency, version):
    ds1 = DataflowRef(id=dsi, agency=agency, version=version)
    ds2 = DataflowRef(id=dsi, agency=agency, version=version)

    assert ds1 == ds2


def test_not_equal(dsi, agency, version):
    ds1 = DataflowRef(id=dsi, agency=agency, version=version)
    ds2 = DataflowRef(
        id=dsi,
        agency=agency,
        version=f"{version}.42",
    )

    assert ds1 != ds2


def test_tostr_id(dsi, agency):
    d = DataflowRef(id=dsi, agency=agency)

    s = str(d)
    expected_str = f"agency: {agency}, id: {dsi}"

    assert s == expected_str
