from pysdmx.toolkit.sqlsrv import get_pagination_clause


def test_no_pagination():
    pagination = get_pagination_clause(0)

    assert pagination == ""


def test_offset():
    pagination = get_pagination_clause(42)

    assert pagination == " OFFSET 42 ROWS"


def test_offset_and_limit():
    pagination = get_pagination_clause(42, 100)

    assert pagination == " OFFSET 42 ROWS FETCH NEXT 100 ROWS ONLY"
