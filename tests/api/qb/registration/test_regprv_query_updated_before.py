from datetime import datetime, timezone

import pytest

from pysdmx.api.qb.registration import RegistrationByProviderQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def updated_before():
    return datetime.now(timezone.utc)


@pytest.fixture
def updated_after():
    return datetime.now(timezone.utc)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_no_default_updated_before(
    api_version: ApiVersion,
):
    expected = f"/registration/provider/*/*"

    q = RegistrationByProviderQuery()
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_updated_before(
    updated_before: datetime,
    api_version: ApiVersion,
):
    expected = (
        "/registration/provider/*/*"
        f'?updatedBefore={updated_before.isoformat("T", "seconds")}'
    )

    q = RegistrationByProviderQuery(updated_before=updated_before)
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
        "/registration/provider/*/*"
        f'?updatedBefore={updated_before.isoformat("T", "seconds")}'
        f'&updatedAfter={updated_after.isoformat("T", "seconds")}'
    )

    q = RegistrationByProviderQuery(
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
        "/registration/provider"
        f'?updatedBefore={updated_before.isoformat("T", "seconds")}'
    )

    q = RegistrationByProviderQuery(updated_before=updated_before)
    url = q.get_url(api_version, True)

    assert url == expected
