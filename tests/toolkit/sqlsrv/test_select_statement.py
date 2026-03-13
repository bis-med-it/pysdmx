import pytest

from pysdmx import errors
from pysdmx.api.dc.query import Operator, SortBy, TextFilter
from pysdmx.toolkit.sqlsrv import get_select_statement


def test_select_statement():
    schema_name = "SDMX"
    table_name = "BOP"
    cols = ["SKEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS"]
    flt = TextFilter("PRV", Operator.EQUALS, "UY2")
    offset = 0
    limit = 42
    srt = SortBy("TIME_PERIOD", "desc")

    select, values = get_select_statement(
        table_name, schema_name, flt, cols, [srt], offset, limit
    )

    assert select == (
        'SELECT "SKEY", "TIME_PERIOD", "OBS_VALUE", "OBS_STATUS" '
        "FROM SDMX.BOP "
        'WHERE "PRV" = ? '
        'ORDER BY "TIME_PERIOD" DESC '
        "OFFSET 0 ROWS "
        "FETCH NEXT 42 ROWS ONLY"
    )
    assert len(values) == 1
    assert values[0] == "UY2"


def test_invalid_schema_name():
    schema_name = '"; DROP TABLE users; --'
    table_name = "orders"

    with pytest.raises(errors.Invalid):
        get_select_statement(table_name, schema_name)


def test_invalid_table_name():
    schema_name = "dbo"
    table_name = 'users" UNION SELECT * FROM passwords --'

    with pytest.raises(errors.Invalid):
        get_select_statement(table_name, schema_name)
