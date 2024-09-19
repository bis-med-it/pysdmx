from parsy import (  # type: ignore[import-untyped]
    alt,
    any_char,
    ParseError,
    regex,
    string,
)

from pysdmx.errors import Invalid

__YEAR4 = string("yyyy").map(lambda x: r"%G")
__YEAR2 = string("yy").map(lambda x: r"%y")
__MONTH_F = string("MMMM").map(lambda x: r"%B")
__MONTH_S = string("MMM").map(lambda x: r"%b")
__MONTH_NUM = string("MM").map(lambda x: r"%m")
__WEEK_Y = string("ww").map(lambda x: r"%V")
__DAY_Y = string("DD").map(lambda x: r"%j")
__DAY_M = string("dd").map(lambda x: r"%d")
__DAY_NUM = string("U").map(lambda x: r"%u")
__DAY_NM_F = string("EEEE").map(lambda x: r"%A")
__DAY_NM_S = regex("^E{1,3}$").map(lambda x: r"%a")
__HOUR_DAY = string("HH").map(lambda x: r"%H")
__HOUR_AP = string("hh").map(lambda x: r"%I")
__MIN = string("mm").map(lambda x: r"%M")
__SEC = string("ss").map(lambda x: r"%S")
__ANY = any_char

__single_parser = alt(
    __YEAR4,
    __YEAR2,
    __MONTH_F,
    __MONTH_S,
    __MONTH_NUM,
    __WEEK_Y,
    __DAY_Y,
    __DAY_M,
    __DAY_NUM,
    __DAY_NM_F,
    __DAY_NM_S,
    __HOUR_DAY,
    __HOUR_AP,
    __MIN,
    __SEC,
    __ANY,
)

__dpm_parser = __single_parser.at_least(1)


def convert_dpm(sdmx_pattern: str) -> str:
    """Convert an SDMX date pattern into Python format codes."""
    unsupported = ["G", "n", "kk", "KK", "S", "W"]
    for i in unsupported:
        if i in sdmx_pattern:
            raise Invalid("Parsing failed", f"Pattern {i} is not supported.")
    try:
        return "".join(__dpm_parser.parse(sdmx_pattern))
    except ParseError as pe:
        raise Invalid("Invalid pattern", f"The error was: {str(pe)}") from pe
