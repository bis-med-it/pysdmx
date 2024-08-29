from pysdmx.util import convert_dpm


def test_full_year():
    out = convert_dpm("yyyy")

    assert out == r"%G"


def test_short_year():
    out = convert_dpm("yy")

    assert out == r"%y"


def test_month_number():
    out = convert_dpm("MM")

    assert out == r"%m"


def test_month_short():
    out = convert_dpm("MMM")

    assert out == r"%b"


def test_month_full():
    out = convert_dpm("MMMM")

    assert out == r"%B"


def test_day_in_year():
    out = convert_dpm("DD")

    assert out == r"%j"


def test_day_in_month():
    out = convert_dpm("dd")

    assert out == r"%d"


def test_day_in_week():
    out = convert_dpm("U")

    assert out == r"%u"


def test_week_in_year():
    out = convert_dpm("ww")

    assert out == r"%V"


def test_hours_24():
    out = convert_dpm("HH")

    assert out == r"%H"


def test_hours_12():
    out = convert_dpm("hh")

    assert out == r"%I"


def test_minutes():
    out = convert_dpm("mm")

    assert out == r"%M"


def test_seconds():
    out = convert_dpm("ss")

    assert out == r"%S"


def test_ddMMyy():
    out = convert_dpm("ddMMyy")

    assert out == r"%d%m%y"
