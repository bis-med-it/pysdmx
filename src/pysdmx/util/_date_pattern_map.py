from parsy import alt, any_char, string

YEAR4 = string("yyyy").map(lambda x: r"%G")
YEAR2 = string("yy").map(lambda x: r"%y")
MONTH_F = string("MMMM").map(lambda x: r"%B")
MONTH_S = string("MMM").map(lambda x: r"%b")
MONTH_NUM = string("MM").map(lambda x: r"%m")
WEEK_Y = string("ww").map(lambda x: r"%V")
DAY_Y = string("DD").map(lambda x: r"%j")
DAY_M = string("dd").map(lambda x: r"%d")
DAY_NUM = string("U").map(lambda x: r"%u")
HOUR_DAY = string("HH").map(lambda x: r"%H")
HOUR_AP = string("hh").map(lambda x: r"%I")
MIN = string("mm").map(lambda x: r"%M")
SEC = string("ss").map(lambda x: r"%S")
ANY = any_char

single_parser = alt(
    YEAR4,
    YEAR2,
    MONTH_F,
    MONTH_S,
    MONTH_NUM,
    WEEK_Y,
    DAY_Y,
    DAY_M,
    DAY_NUM,
    HOUR_DAY,
    HOUR_AP,
    MIN,
    SEC,
    ANY,
)
