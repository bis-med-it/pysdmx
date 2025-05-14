from datetime import datetime, timezone

import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def updated_after():
    return datetime(2011, 6, 17, 10, 42, 21, tzinfo=timezone.utc)


@pytest.fixture
def expected():
    return "2011-06-17T10:42:21+00:00"


@pytest.mark.parametrize("api_version", ApiVersion)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, updated_after="TIME_PERIOD")

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_updated_after_before_2_0_0(
    res: str,
    updated_after: datetime,
    expected: str,
    api_version: ApiVersion,
):
    expected = (
        f"/data/all,{res},latest/all"
        f"?updatedAfter={expected}&detail=full&includeHistory=false"
    )

    q = DataQuery(resource_id=res, updated_after=updated_after)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V2_0_0 and v < ApiVersion.V2_2_0
    ),
)
def test_url_updated_after_since_2_0_0(
    updated_after: datetime,
    expected: str,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?updatedAfter={expected}"
        "&attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(updated_after=updated_after)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_2_0),
)
def test_url_updated_after_since_2_2_0(
    updated_after: datetime,
    expected: str,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?updatedAfter={expected}"
        "&attributes=dsd&measures=all&includeHistory=false&offset=0"
    )

    q = DataQuery(updated_after=updated_after)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_updated_after_before_2_0_0_short(
    res: str,
    updated_after: datetime,
    expected: str,
    api_version: ApiVersion,
):
    expected = f"/data/{res}?updatedAfter={expected}"

    q = DataQuery(resource_id=res, updated_after=updated_after)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_updated_after_since_2_0_0_short(
    updated_after: datetime,
    expected: str,
    api_version: ApiVersion,
):
    expected = f"/data?updatedAfter={expected}"

    q = DataQuery(updated_after=updated_after)
    url = q.get_url(api_version, True)

    assert url == expected
