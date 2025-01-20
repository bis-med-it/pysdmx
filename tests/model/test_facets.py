import pytest

from pysdmx.model import Facets


def test_basic_instantiation():
    f1 = Facets(min_length=2)
    f2 = Facets(max_length=1)

    assert f1.min_length == 2
    assert f1.max_length is None
    assert f1.min_value is None
    assert f1.max_value is None
    assert f1.start_value is None
    assert f1.end_value is None
    assert f1.interval is None
    assert f1.time_interval is None
    assert f1.decimals is None
    assert f1.pattern is None
    assert f1.start_time is None
    assert f1.end_time is None
    assert f1.is_sequence is False
    assert f2.min_length is None
    assert f2.max_length == 1


def test_immutable():
    f = Facets(min_length=2)
    with pytest.raises(AttributeError):
        f.max_length = 3


def test_equal():
    f1 = Facets(min_length=2)
    f2 = Facets(min_length=2)

    assert f1 == f2


def test_not_equal():
    f1 = Facets(min_length=2)
    f2 = Facets(max_length=2)

    assert f1 != f2


def test_tostr():
    f1 = Facets(min_length=2, max_length=3)

    s = str(f1)

    assert s == "min_length=2, max_length=3"
