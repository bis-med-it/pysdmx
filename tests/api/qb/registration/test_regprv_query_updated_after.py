from datetime import datetime, timezone

import pytest

from pysdmx.api.qb.registration import RegistrationByProviderQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def updated_after():
    return datetime.now(timezone.utc)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_no_default_updated_after(
    api_version: ApiVersion,
):
    expected = "/registration/provider/*/*"

    q = RegistrationByProviderQuery()
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_updated_after(
    updated_after: datetime,
    api_version: ApiVersion,
):
    expected = (
        "/registration/provider/*/*"
        f"?updatedAfter={updated_after.isoformat('T', 'seconds')}"
    )

    q = RegistrationByProviderQuery(updated_after=updated_after)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_omit_defaults_updated_after(
    updated_after: datetime, api_version: ApiVersion
):
    expected = (
        "/registration/provider"
        f"?updatedAfter={updated_after.isoformat('T', 'seconds')}"
    )

    q = RegistrationByProviderQuery(updated_after=updated_after)
    url = q.get_url(api_version, True)

    assert url == expected
