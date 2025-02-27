import pytest

from pysdmx.api.qb.schema import (
    SchemaContext,
    SchemaQuery,
)
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def context():
    return SchemaContext.METADATA_STRUCTURE


@pytest.fixture
def agency():
    return "BIS"


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def obs_dim():
    return "TIME_PERIOD"


@pytest.mark.parametrize("api_version", ApiVersion)
def test_url_no_obs_dim_short(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = f"/schema/{context.value}/{agency}/{res}/{version}"

    q = SchemaQuery(context, agency, res, version)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize("api_version", ApiVersion)
def test_url_with_obs_dim_short(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    obs_dim: str,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}"
        f"?dimensionAtObservation={obs_dim}"
    )

    q = SchemaQuery(context, agency, res, version, obs_dim)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_with_obs_dim_full_before_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    obs_dim: str,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}"
        f"?dimensionAtObservation={obs_dim}&explicit=false"
    )

    q = SchemaQuery(context, agency, res, version, obs_dim)
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
def test_url_with_obs_dim_full_since_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    obs_dim: str,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}"
        f"?dimensionAtObservation={obs_dim}"
    )

    q = SchemaQuery(context, agency, res, version, obs_dim)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_2_0),
)
def test_url_with_obs_dim_full_since_2_2_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    obs_dim: str,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}"
        f"?dimensionAtObservation={obs_dim}&deletion=false"
    )

    q = SchemaQuery(context, agency, res, version, obs_dim)
    url = q.get_url(api_version)

    assert url == expected
