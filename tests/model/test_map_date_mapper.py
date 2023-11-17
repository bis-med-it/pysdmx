import pytest

from pysdmx.model import DateMapper


@pytest.fixture()
def source():
    return "DATE"


@pytest.fixture()
def target():
    return "TIME_PERIOD"


@pytest.fixture()
def pattern():
    return "MMM yy"


@pytest.fixture()
def freq():
    return "M"


def test_full_instantiation(source, target, pattern, freq):
    m = DateMapper(source, target, pattern, freq)

    assert m.source == source
    assert m.target == target
    assert m.pattern == pattern
    assert m.frequency == freq


def test_immutable(source, target, pattern, freq):
    m = DateMapper(source, target, pattern, freq)
    with pytest.raises(AttributeError):
        m.frequency = "A"


def test_equal(source, target, pattern, freq):
    m1 = DateMapper(source, target, pattern, freq)
    m2 = DateMapper(source, target, pattern, freq)

    assert m1 == m2


def test_not_equal(source, target, pattern, freq):
    m1 = DateMapper(source, target, pattern, freq)
    m2 = DateMapper(source + "2", target, pattern, freq)

    assert m1 != m2
