from typing import List

import pytest

from pysdmx.api.qb.registration import RegistrationByContextQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def id():
    return "CBS"


@pytest.fixture
def mult_ids():
    return ["CBS", "LBS"]


@pytest.fixture
def agency():
    return "BIS"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_multiple_ids(mult_ids: List[str], api_version: ApiVersion):
    expected = f"/registration/*/*/{','.join(mult_ids)}/*"

    q = RegistrationByContextQuery(resource_id=mult_ids)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_default_id(agency: str, api_version: ApiVersion):
    expected = f"/registration/*/{agency}/*/*"

    q = RegistrationByContextQuery(agency_id=agency)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_single_id(id: str, api_version: ApiVersion):
    expected = f"/registration/*/*/{id}/*"

    q = RegistrationByContextQuery(resource_id=id)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_omit_default_id(agency: str, api_version: ApiVersion):
    expected = f"/registration/*/{agency}"

    q = RegistrationByContextQuery(agency_id=agency)
    url = q.get_url(api_version, True)

    assert url == expected
