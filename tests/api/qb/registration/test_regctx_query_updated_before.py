from datetime import datetime, timedelta, timezone

import pytest

from pysdmx.api.qb.registration import RegistrationByContextQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def updated_after():
    return datetime.now(timezone.utc)


@pytest.fixture
def updated_before():
    b = datetime.now(timezone.utc)
    return b + timedelta(minutes=10)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_no_default_updated_before(api_version: ApiVersion):
    expected = "/registration/*/*/*/*"

    q = RegistrationByContextQuery()
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_updated_before(updated_before: datetime, api_version: ApiVersion):
    expected = (
        "/registration/*/*/*/*"
        f'?updatedBefore={updated_before.isoformat("T", "seconds")}'
    )

    q = RegistrationByContextQuery(updated_before=updated_before)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_updated_before_and_after(
    updated_before: datetime,
    updated_after: datetime,
    api_version: ApiVersion,
):
    expected = (
        "/registration/*/*/*/*"
        f'?updatedBefore={updated_before.isoformat("T", "seconds")}'
        f'&updatedAfter={updated_after.isoformat("T", "seconds")}'
    )

    q = RegistrationByContextQuery(
        updated_before=updated_before, updated_after=updated_after
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_omit_defaults_updated_before(
    updated_before: datetime, api_version: ApiVersion
):
    expected = (
        "/registration"
        f'?updatedBefore={updated_before.isoformat("T", "seconds")}'
    )

    q = RegistrationByContextQuery(updated_before=updated_before)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_updated_consistency(
    updated_before: datetime,
    updated_after: datetime,
    api_version: ApiVersion,
):
    q = RegistrationByContextQuery(
        updated_before=updated_after, updated_after=updated_before
    )

    with pytest.raises(Invalid):
        q.get_url(api_version)
