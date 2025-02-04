from typing import List

import pytest

from pysdmx.api.qb.registration import RegistrationByProviderQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def agency():
    return "BIS"


@pytest.fixture
def mult_agencies():
    return ["BIS", "ECB"]


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_multiple_agencies(
    mult_agencies: List[str],
    api_version: ApiVersion,
):
    expected = f"/registration/provider/{','.join(mult_agencies)}/*"

    q = RegistrationByProviderQuery(mult_agencies)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_default_agency(
    api_version: ApiVersion,
):
    expected = f"/registration/provider/*/*"

    q = RegistrationByProviderQuery()
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_single_agency(
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
def test_url_omit_default_agency(
    api_version: ApiVersion,
):
    expected = f"/registration/provider"

    q = RegistrationByProviderQuery()
    url = q.get_url(api_version, True)

    assert url == expected
