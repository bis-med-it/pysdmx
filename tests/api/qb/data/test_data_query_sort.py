from typing import Sequence

import pytest

from pysdmx.api.dc.query import SortBy
from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def sort():
    return [SortBy("REF_AREA"), SortBy("TIME_PERIOD", "desc")]


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, sort="blah")

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_2_0)
)
def test_invalid_before_2_2_0(
    res: str, sort: Sequence[SortBy], api_version: ApiVersion
):
    q = DataQuery(resource_id=res, sort=sort)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_sort(sort: Sequence[SortBy], api_version: ApiVersion):
    expected = (
        "/data/*/*/*/*/*?"
        "attributes=dsd&measures=all&includeHistory=false&offset=0"
        "&sort=REF_AREA:asc+TIME_PERIOD:desc"
    )

    q = DataQuery(sort=sort)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_sort(sort: Sequence[SortBy], api_version: ApiVersion):
    expected = "/data?sort=REF_AREA:asc+TIME_PERIOD:desc"

    q = DataQuery(sort=sort)
    url = q.get_url(api_version, True)

    assert url == expected
