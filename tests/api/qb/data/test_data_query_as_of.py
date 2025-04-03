from datetime import datetime, timezone

import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def as_of():
    return datetime(2011, 6, 17, 10, 42, 21, tzinfo=timezone.utc)


@pytest.fixture
def expected():
    return "2011-06-17T10:42:21+00:00"


@pytest.mark.parametrize("api_version", ApiVersion)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, as_of="TIME_PERIOD")

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_2_0)
)
def test_invalid_before_2_2_0(
    res: str, as_of: datetime, api_version: ApiVersion
):
    q = DataQuery(resource_id=res, as_of=as_of)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_as_of(
    as_of: datetime,
    expected: str,
    api_version: ApiVersion,
):
    expected = (
        "/data/*/*/*/*/*?"
        "attributes=dsd&measures=all&includeHistory=false&offset=0"
        f"&asOf={expected}"
    )

    q = DataQuery(as_of=as_of)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_as_of(
    as_of: datetime,
    expected: str,
    api_version: ApiVersion,
):
    expected = f"/data?asOf={expected}"

    q = DataQuery(as_of=as_of)
    url = q.get_url(api_version, True)

    assert url == expected
