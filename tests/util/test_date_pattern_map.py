from pysdmx.util._date_pattern_map import single_parser


def test_full_year():
    out = single_parser.parse("yyyy")

    assert out == "%Y"


def test_short_year():
    out = single_parser.parse("yy")

    assert out == r"%y"


def test_month_number():
    out = single_parser.parse("MM")

    assert out == r"%m"


def test_month_short():
    out = single_parser.parse("MMM")

    assert out == r"%b"


def test_month_full():
    out = single_parser.parse("MMMM")

    assert out == r"%B"


def test_day_in_year():
    out = single_parser.parse("DD")

    assert out == r"%j"


def test_day_in_month():
    out = single_parser.parse("dd")

    assert out == r"%d"


def test_day_in_week():
    out = single_parser.parse("U")

    assert out == r"%u"


def test_week_in_year():
    out = single_parser.parse("ww")

    assert out == r"%U"


def test_hours_24():
    out = single_parser.parse("HH")

    assert out == r"%H"


def test_hours_12():
    out = single_parser.parse("hh")

    assert out == r"%I"


def test_minutes():
    out = single_parser.parse("mm")

    assert out == r"%M"


def test_seconds():
    out = single_parser.parse("ss")

    assert out == r"%S"


# G Era designator Text AD
# n Number of periods, used after a SDMX
# kk Hour in day (1-24) Number 24
# KK Hour in am/pm (0-11) Number 0
# S Millisecond Number 978

# W Week in month Number 2
# F Day of week in month Number 2
# E Day name in week Text Tuesday; Tue
