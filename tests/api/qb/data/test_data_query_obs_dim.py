import pytest

from pysdmx.api.qb.data import DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def obs_dim():
    return "TIME_PERIOD"


@pytest.mark.parametrize("api_version", ApiVersion)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = DataQuery(resource_id=res, obs_dimension=42)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_obs_dim_before_2_0_0(
    res: str,
    obs_dim: str,
    api_version: ApiVersion,
):
    expected = (
        f"/data/all,{res},latest/all"
        f"?dimensionAtObservation={obs_dim}&detail=full&includeHistory=false"
    )

    q = DataQuery(resource_id=res, obs_dimension=obs_dim)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_obs_dim_since_2_0_0(
    obs_dim: str,
    api_version: ApiVersion,
):
    expected = (
        f"/data/*/*/*/*/*?dimensionAtObservation={obs_dim}"
        "&attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(obs_dimension=obs_dim)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_obs_dim_before_2_0_0_short(
    res: str,
    obs_dim: str,
    api_version: ApiVersion,
):
    expected = f"/data/{res}?dimensionAtObservation={obs_dim}"

    q = DataQuery(resource_id=res, obs_dimension=obs_dim)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_obs_dim_since_2_0_0_short(
    obs_dim: str,
    api_version: ApiVersion,
):
    expected = f"/data?dimensionAtObservation={obs_dim}"

    q = DataQuery(obs_dimension=obs_dim)
    url = q.get_url(api_version, True)

    assert url == expected
