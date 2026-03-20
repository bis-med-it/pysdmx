import pytest

from pysdmx import errors
from pysdmx.api.dc.query import (
    BooleanFilter,
    LogicalOperator,
    MultiFilter,
    NotFilter,
    NullFilter,
    NumberFilter,
    Operator,
    TextFilter,
)
from pysdmx.toolkit.sqlsrv import get_where_clause


def test_no_filter():
    where, value = get_where_clause(None)

    assert where == ""
    assert value == []


def test_text_filter_contains():
    f = TextFilter("name", Operator.LIKE, r"%abc%")

    where, values = get_where_clause(f)

    assert where == ' WHERE UPPER("name") LIKE ?'
    assert len(values) == 1
    assert values[0] == r"%ABC%"


def test_text_filter_notcontains():
    f = TextFilter("name", Operator.NOT_LIKE, r"%abc%")

    where, values = get_where_clause(f)

    assert where == ' WHERE UPPER("name") NOT LIKE ?'
    assert len(values) == 1
    assert values[0] == r"%ABC%"


def test_text_filter_equals():
    f = TextFilter("name", Operator.EQUALS, "abc")

    where, values = get_where_clause(f)

    assert where == ' WHERE "name" = ?'
    assert len(values) == 1
    assert values[0] == "abc"


def test_text_filter_notequal():
    f = TextFilter("name", Operator.NOT_EQUALS, "abc")

    where, values = get_where_clause(f)

    assert where == ' WHERE "name" <> ?'
    assert len(values) == 1
    assert values[0] == "abc"


def test_text_filter_not():
    f = NotFilter(TextFilter("name", Operator.EQUALS, "abc"))

    where, values = get_where_clause(f)

    assert where == ' WHERE NOT("name" = ?)'
    assert len(values) == 1
    assert values[0] == "abc"


def test_text_filter_startswith():
    f = TextFilter("name", Operator.LIKE, r"abc%")

    where, values = get_where_clause(f)

    assert where == ' WHERE UPPER("name") LIKE ?'
    assert len(values) == 1
    assert values[0] == r"ABC%"


def test_text_filter_endswith():
    f = TextFilter("name", Operator.LIKE, r"%abc")

    where, values = get_where_clause(f)

    assert where == ' WHERE UPPER("name") LIKE ?'
    assert len(values) == 1
    assert values[0] == r"%ABC"


def test_text_filter_blank():
    f = NullFilter("name", Operator.NULL)

    where, values = get_where_clause(f)

    assert where == ' WHERE "name" IS NULL'
    assert len(values) == 0


def test_text_filter_notblank():
    f = NullFilter("name", Operator.NOT_NULL)

    where, values = get_where_clause(f)

    assert where == ' WHERE "name" IS NOT NULL'
    assert len(values) == 0


def test_multi_filters():
    f1 = TextFilter("name", Operator.LIKE, r"%abc")
    f2 = TextFilter("status", Operator.NOT_EQUALS, "R")
    f3 = MultiFilter([f1, f2])

    where, values = get_where_clause(f3)

    assert where == ' WHERE UPPER("name") LIKE ? AND "status" <> ?'
    assert len(values) == 2
    assert values[0] == r"%ABC"
    assert values[1] == "R"


def test_multi_or_filters():
    f1 = TextFilter("name", Operator.LIKE, r"%abc")
    f2 = TextFilter("status", Operator.IN, ["A", "B"])
    f3 = MultiFilter([f1, f2])
    f4 = TextFilter("prv_id", Operator.EQUALS, "5B0")
    f5 = MultiFilter([f3, f4], LogicalOperator.OR)

    where, values = get_where_clause(f5)

    assert where == (
        ' WHERE (UPPER("name") LIKE ? AND "status" IN (?,?)) OR "prv_id" = ?'
    )
    assert len(values) == 4
    assert values[0] == r"%ABC"
    assert values[1] == "A"
    assert values[2] == "B"
    assert values[3] == "5B0"


def test_in_set_filter():
    f = TextFilter("year", Operator.IN, ["2009", "2016", "2019"])

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" IN (?,?,?)'
    assert len(values) == 3
    assert values[0] == "2009"
    assert values[1] == "2016"
    assert values[2] == "2019"


def test_not_in_set_filter():
    f = TextFilter("year", Operator.NOT_IN, ["2009", "2016", "2019"])

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" NOT IN (?,?,?)'
    assert len(values) == 3
    assert values[0] == "2009"
    assert values[1] == "2016"
    assert values[2] == "2019"


def test_number_filter_equals():
    f = NumberFilter("year", Operator.EQUALS, 2000)

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" = ?'
    assert values[0] == 2000


def test_number_filter_notequal():
    f = NumberFilter("year", Operator.NOT_EQUALS, 2000)

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" <> ?'
    assert values[0] == 2000


def test_number_filter_gt():
    f = NumberFilter("year", Operator.GREATER_THAN, 2000)

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" > ?'
    assert values[0] == 2000


def test_number_filter_gte():
    f = NumberFilter("year", Operator.GREATER_THAN_OR_EQUAL, 2000)

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" >= ?'
    assert values[0] == 2000


def test_number_filter_lt():
    f = NumberFilter("year", Operator.LESS_THAN, 2000)

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" < ?'
    assert values[0] == 2000


def test_number_filter_lte():
    f = NumberFilter("year", Operator.LESS_THAN_OR_EQUAL, 2000)

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" <= ?'
    assert values[0] == 2000


def test_number_filter_in_range():
    f = NumberFilter("year", Operator.BETWEEN, [2009, 2016])

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" BETWEEN ? AND ?'
    assert len(values) == 2
    assert values[0] == 2009
    assert values[1] == 2016


def test_number_filter_not_in_range():
    f = NumberFilter("year", Operator.NOT_BETWEEN, [2009, 2016])

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" NOT BETWEEN ? AND ?'
    assert len(values) == 2
    assert values[0] == 2009
    assert values[1] == 2016


def test_boolean_filter_true():
    f = BooleanFilter("HAS_INV", Operator.EQUALS, True)

    where, values = get_where_clause(f)

    assert where == ' WHERE "HAS_INV" = TRUE'
    assert len(values) == 0


def test_boolean_filter_false():
    f = BooleanFilter("HAS_INV", Operator.EQUALS, False)

    where, values = get_where_clause(f)

    assert where == ' WHERE "HAS_INV" = FALSE'
    assert len(values) == 0


def test_boolean_filter_not_true():
    f = BooleanFilter("HAS_INV", Operator.NOT_EQUALS, True)

    where, values = get_where_clause(f)

    assert where == ' WHERE "HAS_INV" <> TRUE'
    assert len(values) == 0


def test_boolean_filter_not_false():
    f = BooleanFilter("HAS_INV", Operator.NOT_EQUALS, False)

    where, values = get_where_clause(f)

    assert where == ' WHERE "HAS_INV" <> FALSE'
    assert len(values) == 0


def test_boolean_filter_wrong_op():
    f = BooleanFilter("HAS_INV", Operator.GREATER_THAN, False)

    with pytest.raises(errors.Invalid):
        get_where_clause(f)


def test_date_filter_gt():
    f = TextFilter("year", Operator.GREATER_THAN, "2000-01-01")

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" > ?'
    assert values[0] == "2000-01-01"


def test_date_filter_gte():
    f = TextFilter("year", Operator.GREATER_THAN_OR_EQUAL, "2000-01-01")

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" >= ?'
    assert values[0] == "2000-01-01"


def test_date_filter_lt():
    f = TextFilter("year", Operator.LESS_THAN, "2000-01-01")

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" < ?'
    assert values[0] == "2000-01-01"


def test_date_filter_lte():
    f = TextFilter("year", Operator.LESS_THAN_OR_EQUAL, "2000-01-01")

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" <= ?'
    assert values[0] == "2000-01-01"


def test_date_filter_range():
    f = TextFilter("year", Operator.BETWEEN, ["2000-01-01", "2016-01-01"])

    where, values = get_where_clause(f)

    assert where == ' WHERE "year" BETWEEN ? AND ?'
    assert len(values) == 2
    assert values[0] == "2000-01-01"
    assert values[1] == "2016-01-01"
