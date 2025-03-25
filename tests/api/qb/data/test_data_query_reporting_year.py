from datetime import datetime

import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def reporting_year_start_day():
    return "--07-01"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, reporting_year_start_day=42)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_2_0)
)
def test_invalid_before_2_2_0(
    res: str, reporting_year_start_day: datetime, api_version: ApiVersion
):
    q = DataQuery(
        resource_id=res, reporting_year_start_day=reporting_year_start_day
    )

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_reporting_year_start_day(
    reporting_year_start_day: datetime,
    api_version: ApiVersion,
):
    expected = (
        "/data/*/*/*/*/*?"
        "attributes=dsd&measures=all&includeHistory=false"
        f"&reportingYearStartDay={reporting_year_start_day}"
    )

    q = DataQuery(reporting_year_start_day=reporting_year_start_day)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_reporting_year_start_day(
    reporting_year_start_day: datetime,
    api_version: ApiVersion,
):
    expected = f"/data?reportingYearStartDay={reporting_year_start_day}"

    q = DataQuery(reporting_year_start_day=reporting_year_start_day)
    url = q.get_url(api_version, True)

    assert url == expected
