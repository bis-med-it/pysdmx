from typing import List

import pytest

from pysdmx.api.qb.registration import RegistrationByContextQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def mult_versions():
    return ["1.0", "2.1"]


@pytest.fixture
def id():
    return "CBS"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_multiple_versions(
    mult_versions: List[str], api_version: ApiVersion
):
    expected = f"/registration/*/*/*/{','.join(mult_versions)}"

    q = RegistrationByContextQuery(version=mult_versions)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_default_version(id: str, api_version: ApiVersion):
    expected = f"/registration/*/*/{id}/*"

    q = RegistrationByContextQuery(resource_id=id)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_single_version(version: str, api_version: ApiVersion):
    expected = f"/registration/*/*/*/{version}"

    q = RegistrationByContextQuery(version=version)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_omit_default_version(id: str, api_version: ApiVersion):
    expected = f"/registration/*/*/{id}"

    q = RegistrationByContextQuery(resource_id=id)
    url = q.get_url(api_version, True)

    assert url == expected
