from typing import List

import pytest

from pysdmx.api.qb.data import DataContext
from pysdmx.api.qb.registration import RegistrationByContextQuery
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def agency():
    return "BIS"


@pytest.fixture
def mult_agencies():
    return ["BIS", "ECB"]


@pytest.fixture
def context():
    return DataContext.DATAFLOW


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_multiple_agencies(
    mult_agencies: List[str], api_version: ApiVersion
):
    expected = f"/registration/*/{','.join(mult_agencies)}/*/*"

    q = RegistrationByContextQuery(agency_id=mult_agencies)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_1_0),
)
def test_url_default_agency(api_version: ApiVersion):
    expected = "/registration/*/*/*/*"

    q = RegistrationByContextQuery()
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_single_agency(agency: str, api_version: ApiVersion):
    expected = f"/registration/*/{agency}/*/*"

    q = RegistrationByContextQuery(agency_id=agency)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_1_0)
)
def test_url_omit_default_agency(
    context: DataContext, api_version: ApiVersion
):
    expected = f"/registration/{context.value}"

    q = RegistrationByContextQuery(context)
    url = q.get_url(api_version, True)

    assert url == expected
