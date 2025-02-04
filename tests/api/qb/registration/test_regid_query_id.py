from typing import List

import pytest

from pysdmx.api.qb.registration import RegistrationByIdQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def id():
    return "XYZ123"


@pytest.fixture
def mult_id():
    return ["XYZ123", "ABC345"]


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_multiple_ids(
    mult_id: List[str],
    api_version: ApiVersion,
):
    expected = f"/registration/id/{','.join(mult_id)}"

    q = RegistrationByIdQuery(mult_id)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_default_id(
    api_version: ApiVersion,
):
    expected = f"/registration/id/*"

    q = RegistrationByIdQuery()
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_single_id(
    id: str,
    api_version: ApiVersion,
):
    expected = f"/registration/id/{id}"

    q = RegistrationByIdQuery(id)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_omit_default_id(
    api_version: ApiVersion,
):
    expected = f"/registration/id"

    q = RegistrationByIdQuery()
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_1_0)
)
def test_registration_query_before_2_1_0(api_version: ApiVersion):
    q = RegistrationByIdQuery()

    with pytest.raises(Invalid):
        q.get_url(api_version)
