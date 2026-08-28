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


def test_select_statement_case_mode_sensitive():
    schema_name = "SDMX"
    table_name = "BOP"
    cols = ["SKEY", "TIME_PERIOD"]
    flt = TextFilter("PRV", Operator.LIKE, "uy%")

    select, values = get_select_statement(
        table_name,
        schema_name,
        flt,
        cols,
        case_mode="sensitive",
    )

    assert select == (
        'SELECT "SKEY", "TIME_PERIOD" FROM SDMX.BOP WHERE "PRV" LIKE ?'
    )
    assert len(values) == 1
    assert values[0] == "uy%"


def test_select_statement_case_mode_insensitive():
    schema_name = "SDMX"
    table_name = "BOP"
    cols = ["SKEY"]
    flt = TextFilter("PRV", Operator.LIKE, "uy%")

    select, values = get_select_statement(
        table_name,
        schema_name,
        flt,
        cols,
        case_mode="insensitive",
    )

    assert select == 'SELECT "SKEY" FROM SDMX.BOP WHERE UPPER("PRV") LIKE ?'
    assert len(values) == 1
    assert values[0] == "UY%"


def test_select_statement_case_mode_default():
    schema_name = "SDMX"
    table_name = "BOP"
    cols = ["SKEY"]
    flt = TextFilter("PRV", Operator.NOT_LIKE, "uy%")

    select, values = get_select_statement(
        table_name,
        schema_name,
        flt,
        cols,
        case_mode="default",
    )

    assert select == 'SELECT "SKEY" FROM SDMX.BOP WHERE "PRV" NOT LIKE ?'
    assert len(values) == 1
    assert values[0] == "uy%"


def test_select_statement_invalid_case_mode():
    schema_name = "SDMX"
    table_name = "BOP"

    with pytest.raises(errors.Invalid):
        get_select_statement(table_name, schema_name, case_mode="mixed")


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
