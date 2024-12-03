import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def first_n():
    return 1


@pytest.fixture
def last_n():
    return 2


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_last_n_before_2_0_0(
    res: str,
    first_n: int,
    last_n: int,
    api_version: ApiVersion,
):
    expected = (
        f"/data/all,{res},latest/all"
        f"?firstNObservations={first_n}&lastNObservations={last_n}"
        "&detail=full&includeHistory=false"
    )

    q = DataQuery(resource_id=res, first_n_obs=first_n, last_n_obs=last_n)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_last_n_since_2_0_0(
    first_n: int,
    last_n: int,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*"
        f"?firstNObservations={first_n}&lastNObservations={last_n}"
        "&attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(first_n_obs=first_n, last_n_obs=last_n)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_both_n_before_2_0_0_short(
    res: str,
    first_n: int,
    last_n: int,
    api_version: ApiVersion,
):
    expected = (
        f"/data/{res}?firstNObservations={first_n}"
        f"&lastNObservations={last_n}"
    )

    q = DataQuery(resource_id=res, first_n_obs=first_n, last_n_obs=last_n)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_both_n_since_2_0_0_short(
    first_n: int,
    last_n: int,
    api_version: ApiVersion,
):
    exp = f"/data?firstNObservations={first_n}&lastNObservations={last_n}"
    q = DataQuery(first_n_obs=first_n, last_n_obs=last_n)
    url = q.get_url(api_version, True)

    assert url == exp
