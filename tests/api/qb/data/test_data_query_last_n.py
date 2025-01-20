import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def last_n():
    return 2


@pytest.mark.parametrize("api_version", ApiVersion)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, last_n_obs=-1)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_last_n_before_2_0_0(
    res: str,
    last_n: int,
    api_version: ApiVersion,
):
    expected = (
        f"/data/all,{res},latest/all"
        f"?lastNObservations={last_n}&detail=full&includeHistory=false"
    )

    q = DataQuery(resource_id=res, last_n_obs=last_n)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_last_n_since_2_0_0(
    last_n: int,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?lastNObservations={last_n}"
        "&attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(last_n_obs=last_n)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_last_n_before_2_0_0_short(
    res: str,
    last_n: int,
    api_version: ApiVersion,
):
    expected = f"/data/{res}?lastNObservations={last_n}"

    q = DataQuery(resource_id=res, last_n_obs=last_n)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_last_n_since_2_0_0_short(
    last_n: int,
    api_version: ApiVersion,
):
    expected = f"/data?lastNObservations={last_n}"

    q = DataQuery(last_n_obs=last_n)
    url = q.get_url(api_version, True)

    assert url == expected
