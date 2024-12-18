import pytest

from pysdmx.api.dc.query import SortBy


@pytest.fixture()
def comp():
    return "TIME_PERIOD"


@pytest.fixture()
def order():
    return "desc"


def test_basic_instantiation(comp):
    i = SortBy(comp)

    assert i.component == comp
    assert i.order == "asc"


def test_full_instantiation(comp, order):
    i = SortBy(comp, order)

    assert i.component == comp
    assert i.order == order
