import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def limit():
    return 800


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, limit=-2)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_2_0)
)
def test_invalid_before_2_2_0(res: str, limit: int, api_version: ApiVersion):
    q = DataQuery(resource_id=res, limit=limit)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_limit(limit: int, api_version: ApiVersion):
    expected = (
        "/data/*/*/*/*/*?"
        "attributes=dsd&measures=all&includeHistory=false&offset=0"
        f"&limit={limit}"
    )

    q = DataQuery(limit=limit)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_limit(limit: int, api_version: ApiVersion):
    expected = f"/data?limit={limit}"

    q = DataQuery(limit=limit)
    url = q.get_url(api_version, True)

    assert url == expected
