import pytest

from pysdmx.model import DatePatternMap


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


@pytest.fixture()
def pattern_type():
    return "variable"


@pytest.fixture()
def map_id():
    return "my_id"


@pytest.fixture()
def locale():
    return "es"


def test_default_instantiation(source, target, pattern, freq):
    m = DatePatternMap(source, target, pattern, freq)

    assert m.source == source
    assert m.target == target
    assert m.pattern == pattern
    assert m.frequency == freq
    assert m.pattern_type == "fixed"
    assert m.locale == "en"
    assert m.id is None


def test_full_instantiation(
    source, target, pattern, freq, map_id, locale, pattern_type
):
    m = DatePatternMap(
        source, target, pattern, freq, map_id, locale, pattern_type
    )

    assert m.source == source
    assert m.target == target
    assert m.pattern == pattern
    assert m.frequency == freq
    assert m.pattern_type == pattern_type
    assert m.id == map_id
    assert m.locale == locale


def test_immutable(source, target, pattern, freq):
    m = DatePatternMap(source, target, pattern, freq)
    with pytest.raises(AttributeError):
        m.frequency = "A"


def test_equal(source, target, pattern, freq):
    m1 = DatePatternMap(source, target, pattern, freq)
    m2 = DatePatternMap(source, target, pattern, freq)

    assert m1 == m2


def test_not_equal(source, target, pattern, freq):
    m1 = DatePatternMap(source, target, pattern, freq)
    m2 = DatePatternMap(source + "2", target, pattern, freq)

    assert m1 != m2


def test_pypattern_ddMMyy(source, target, freq):
    m = DatePatternMap(source, target, "ddMMyy", freq)

    assert m.py_pattern == r"%d%m%y"


def test_pypattern_MMddyyyy(source, target, freq):
    m = DatePatternMap(source, target, "MM/dd/yyyy", freq)

    assert m.py_pattern == r"%m/%d/%Y"


def test_pypattern_MMMyyyy(source, target, freq):
    m = DatePatternMap(source, target, "MMM yyyy", freq)

    assert m.py_pattern == r"%b %Y"
