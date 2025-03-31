import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def first_n():
    return 1


@pytest.mark.parametrize("api_version", ApiVersion)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, first_n_obs=-1)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_first_n_before_2_0_0(
    res: str,
    first_n: int,
    api_version: ApiVersion,
):
    expected = (
        f"/data/all,{res},latest/all"
        f"?firstNObservations={first_n}&detail=full&includeHistory=false"
    )

    q = DataQuery(resource_id=res, first_n_obs=first_n)
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
def test_url_first_n_since_2_0_0(
    first_n: int,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?firstNObservations={first_n}"
        "&attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(first_n_obs=first_n)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_first_n_since_2_2_0(
    first_n: int,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?firstNObservations={first_n}"
        "&attributes=dsd&measures=all&includeHistory=false&offset=0"
    )

    q = DataQuery(first_n_obs=first_n)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_first_n_before_2_0_0_short(
    res: str,
    first_n: int,
    api_version: ApiVersion,
):
    expected = f"/data/{res}?firstNObservations={first_n}"

    q = DataQuery(resource_id=res, first_n_obs=first_n)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_first_n_since_2_0_0_short(
    first_n: int,
    api_version: ApiVersion,
):
    expected = f"/data?firstNObservations={first_n}"

    q = DataQuery(first_n_obs=first_n)
    url = q.get_url(api_version, True)

    assert url == expected
