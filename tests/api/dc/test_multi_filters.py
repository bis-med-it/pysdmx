from pysdmx.api.dc.query._model import (
    DateTimeFilter,
    LogicalOperator,
    MultiFilter,
    Operator,
    TextFilter,
)


def test_create_simple_mf():
    flt1 = TextFilter("REF_AREA", Operator.EQUALS, "UY")
    flt2 = DateTimeFilter("TIME_PERIOD", Operator.GREATER_THAN, "2000-01")

    mf = MultiFilter([flt1, flt2])

    assert len(mf.filters) == 2
    assert flt1 in mf.filters
    assert flt2 in mf.filters
    assert mf.operator == LogicalOperator.AND


def test_create_nested_mf():
    flt1 = TextFilter("REF_AREA", Operator.EQUALS, "UY")
    flt2 = TextFilter("REF_AREA", Operator.EQUALS, "AR")
    flt3 = DateTimeFilter("TIME_PERIOD", Operator.GREATER_THAN, "2000-01")
    mf1 = MultiFilter([flt1, flt2], LogicalOperator.OR)

    mf = MultiFilter([mf1, flt3])

    assert len(mf.filters) == 2
    assert mf1 in mf.filters
    assert flt3 in mf.filters
    assert mf.operator == LogicalOperator.AND
    cflt = mf.filters[0]
    assert len(cflt.filters) == 2
    assert flt1 in cflt.filters
    assert flt2 in cflt.filters
    assert cflt.operator == LogicalOperator.OR
