import pytest

from pysdmx.api.dc.query import (
    LogicalOperator,
    MultiFilter,
    NotFilter,
    NumberFilter,
    Operator,
    TextFilter,
)
from pysdmx.api.qb.availability import AvailabilityQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_availability_components_v1(api_version: ApiVersion):
    flt = TextFilter("FREQ", Operator.EQUALS, "M")
    q = AvailabilityQuery(resource_id="CBS", components=flt)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_unsupported_operator(api_version: ApiVersion):
    flt = TextFilter("FREQ", Operator.NOT_IN, ["A", "M"])
    q = AvailabilityQuery(components=flt)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_eq(api_version: ApiVersion):
    flt = TextFilter("FREQ", Operator.EQUALS, "M")
    expected = "/availability/*/*/*/*/*/*?c[FREQ]=M&references=none&mode=exact"

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_ne(api_version: ApiVersion):
    flt = TextFilter("FREQ", Operator.NOT_EQUALS, "M")
    expected = (
        "/availability/*/*/*/*/*/*?c[FREQ]=ne:M&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_lt(api_version: ApiVersion):
    flt = TextFilter("TIME_PERIOD", Operator.LESS_THAN, "2011")
    expected = (
        "/availability/*/*/*/*/*/*?c[TIME_PERIOD]=lt:2011"
        "&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_le(api_version: ApiVersion):
    flt = TextFilter("TIME_PERIOD", Operator.LESS_THAN_OR_EQUAL, "2011")
    expected = (
        "/availability/*/*/*/*/*/*?c[TIME_PERIOD]=le:2011"
        "&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_gt(api_version: ApiVersion):
    flt = TextFilter("TIME_PERIOD", Operator.GREATER_THAN, "2011")
    expected = (
        "/availability/*/*/*/*/*/*?c[TIME_PERIOD]=gt:2011"
        "&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_ge(api_version: ApiVersion):
    flt = TextFilter("TIME_PERIOD", Operator.GREATER_THAN_OR_EQUAL, "2011")
    expected = (
        "/availability/*/*/*/*/*/*?c[TIME_PERIOD]=ge:2011"
        "&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_co(api_version: ApiVersion):
    flt = TextFilter("FREQ", Operator.LIKE, "%M%")
    expected = (
        "/availability/*/*/*/*/*/*?c[FREQ]=co:M&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_nc(api_version: ApiVersion):
    flt = TextFilter("FREQ", Operator.NOT_LIKE, "%M%")
    expected = (
        "/availability/*/*/*/*/*/*?c[FREQ]=nc:M&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_sw(api_version: ApiVersion):
    flt = TextFilter("TITLE", Operator.LIKE, "ICP%")
    expected = (
        "/availability/*/*/*/*/*/*?c[TITLE]=sw:ICP&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_ew(api_version: ApiVersion):
    flt = TextFilter("TITLE", Operator.LIKE, "%ICP")
    expected = (
        "/availability/*/*/*/*/*/*?c[TITLE]=ew:ICP&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_wrong_like(api_version: ApiVersion):
    flt = TextFilter("FREQ", Operator.LIKE, "M")

    q = AvailabilityQuery(components=flt)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_wrong_like_type(api_version: ApiVersion):
    flt = NumberFilter("VALUE", Operator.LIKE, 42)

    q = AvailabilityQuery(components=flt)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_text_comp_in(api_version: ApiVersion):
    flt = TextFilter("FREQ", Operator.IN, ["A", "M"])
    expected = (
        "/availability/*/*/*/*/*/*?c[FREQ]=A,M&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_number(api_version: ApiVersion):
    flt = NumberFilter("OBS_VALUE", Operator.GREATER_THAN, 2)
    expected = (
        "/availability/*/*/*/*/*/*?c[OBS_VALUE]=gt:2"
        "&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_one_number_between(api_version: ApiVersion):
    flt = NumberFilter("OBS_VALUE", Operator.BETWEEN, [2, 8])
    expected = (
        "/availability/*/*/*/*/*/*?c[OBS_VALUE]=ge:2+le:8"
        "&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=flt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_mult_filters(api_version: ApiVersion):
    flt1 = TextFilter("COUNTRY", Operator.IN, value=["AR", "UY"])
    flt2 = TextFilter("PERIOD", Operator.GREATER_THAN_OR_EQUAL, "2024")
    flt3 = NumberFilter("VALUE", Operator.LESS_THAN, 42)
    mflt = MultiFilter([flt1, flt2, flt3])
    expected = (
        "/availability/*/*/*/*/*/*?"
        "c[COUNTRY]=AR,UY&c[PERIOD]=ge:2024&c[VALUE]=lt:42"
        "&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=mflt)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_mult_or_filters(api_version: ApiVersion):
    flt1 = TextFilter("COUNTRY", Operator.IN, value=["AR", "UY"])
    flt2 = TextFilter("PERIOD", Operator.GREATER_THAN_OR_EQUAL, "2024")
    mflt = MultiFilter([flt1, flt2], LogicalOperator.OR)

    q = AvailabilityQuery(components=mflt)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_mult_filters_wrong_type(api_version: ApiVersion):
    flt1 = TextFilter("COUNTRY", Operator.EQUALS, value="AR")
    flt2 = NotFilter(flt1)
    flt3 = TextFilter("PERIOD", Operator.GREATER_THAN_OR_EQUAL, "2024")
    mflt = MultiFilter([flt2, flt3])

    q = AvailabilityQuery(components=mflt)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_mult_same_comp(api_version: ApiVersion):
    flt1 = TextFilter("COUNTRY", Operator.EQUALS, value="AR")
    flt2 = TextFilter("PERIOD", Operator.GREATER_THAN_OR_EQUAL, "2020")
    flt3 = TextFilter("PERIOD", Operator.LESS_THAN, "2024")
    mflt = MultiFilter([flt1, flt2, flt3])
    expected = (
        "/availability/*/*/*/*/*/*?c[COUNTRY]=AR&c[PERIOD]=ge:2020+lt:2024"
        "&references=none&mode=exact"
    )

    q = AvailabilityQuery(components=mflt)
    url = q.get_url(api_version)

    assert url == expected
