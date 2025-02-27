from datetime import datetime, timezone

import pytest

from pysdmx.api.qb.schema import (
    SchemaContext,
    SchemaQuery,
)
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


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


@pytest.fixture
def as_of():
    return datetime(2025, 1, 1, 12, 42, 21, tzinfo=timezone.utc)


@pytest.fixture
def deletion():
    return True


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_deletion(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    deletion: bool,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}?deletion=true"
    )

    q = SchemaQuery(context, agency, res, version, deletion=deletion)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_deletion_and_obs_dim(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    obs_dim: str,
    deletion: bool,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}"
        f"?dimensionAtObservation={obs_dim}&deletion=true"
    )

    q = SchemaQuery(context, agency, res, version, obs_dim, deletion=deletion)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_2_0)
)
def test_url_deletion_before_2_2_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    obs_dim: str,
    deletion: bool,
    api_version: ApiVersion,
):
    q = SchemaQuery(context, agency, res, version, obs_dim, deletion=deletion)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_deletion_since_2_2_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    obs_dim: str,
    as_of: datetime,
    deletion: bool,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}"
        f"?dimensionAtObservation={obs_dim}"
        "&asOf=2025-01-01T12:42:21+00:00&deletion=true"
    )

    q = SchemaQuery(
        context, agency, res, version, obs_dim, as_of=as_of, deletion=deletion
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_deletion_no_obs_dim_since_2_2_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    as_of: datetime,
    deletion: bool,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}"
        "?asOf=2025-01-01T12:42:21+00:00&deletion=true"
    )

    q = SchemaQuery(
        context, agency, res, version, as_of=as_of, deletion=deletion
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_deletion_defaults_to_false(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}?deletion=false"
    )

    q = SchemaQuery(context, agency, res, version)
    url = q.get_url(api_version)

    assert url == expected
