from pysdmx.api.dc.query import SortBy
from pysdmx.toolkit.sqlsrv import get_sort_clause


def test_no_sort():
    sort = get_sort_clause([])

    assert sort == ""


def test_one_sort():
    sort = get_sort_clause([SortBy("TIME_PERIOD")])

    assert sort == ' ORDER BY "TIME_PERIOD" ASC'


def test_multiple_sorts():
    sort = get_sort_clause(
        [SortBy("TIME_PERIOD"), SortBy("OBS_VALUE", "desc")]
    )

    assert sort == ' ORDER BY "TIME_PERIOD" ASC, "OBS_VALUE" DESC'
