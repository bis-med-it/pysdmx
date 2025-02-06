from typing import List

import pytest

from pysdmx.api.qb.registration import RegistrationByProviderQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def agency():
    return "BIS"


@pytest.fixture
def prv():
    return "4F0"


@pytest.fixture
def mult_prvs():
    return ["4F0", "5B0"]


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_multiple_providers(
    mult_prvs: List[str],
    api_version: ApiVersion,
):
    expected = f"/registration/provider/*/{','.join(mult_prvs)}"

    q = RegistrationByProviderQuery(provider_id=mult_prvs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_default_provider(
    agency: str,
    api_version: ApiVersion,
):
    expected = f"/registration/provider/{agency}/*"

    q = RegistrationByProviderQuery(agency)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_single_provider(
    prv: str,
    api_version: ApiVersion,
):
    expected = f"/registration/provider/*/{prv}"

    q = RegistrationByProviderQuery(provider_id=prv)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_omit_default_provider(
    agency: str,
    api_version: ApiVersion,
):
    expected = f"/registration/provider/{agency}"

    q = RegistrationByProviderQuery(agency)
    url = q.get_url(api_version, True)

    assert url == expected
