from typing import List

import pytest

from pysdmx.api.qb.data import DataContext, DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import ClientError


@pytest.fixture()
def context():
    return DataContext.DATAFLOW


@pytest.fixture()
def agency():
    return "SDMX"


@pytest.fixture()
def agencies():
    return ["BIS", "SDMX"]


@pytest.fixture()
def res():
    return "REF_META"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_multiple_agencies_before_2_0_0(
    context: DataContext, agencies: List[str], api_version: ApiVersion
):
    q = DataQuery(context, agencies)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_agencies_since_2_0_0(
    context: DataContext, agencies: List[str], api_version: ApiVersion
):
    expected = (
        f"/data/{context.value}/{','.join(agencies)}/*/*/*"
        f"?attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(context, agencies)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_agencies_since_2_0_0_short(
    agencies: List[str], api_version: ApiVersion
):
    expected = f"/data/*/{','.join(agencies)}"

    q = DataQuery(agency_id=agencies)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_url_default_agency_before_2_0_0(
    context: DataContext, res: str, api_version: ApiVersion
):
    expected = f"/data/all,{res},latest/all?detail=full&includeHistory=false"

    q = DataQuery(context, resource_id=res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_agency_since_2_0_0(
    context: DataContext, api_version: ApiVersion
):
    expected = (
        f"/data/{context.value}/*/*/*/*"
        "?attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(context)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_single_agency_before_2_0_0(
    context: DataContext, agency: str, res: str, api_version: ApiVersion
):
    expected = (
        f"/data/{agency},{res},latest/all?detail=full&includeHistory=false"
    )

    q = DataQuery(context, agency, res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_agency_since_2_0_0(
    context: DataContext, agency: str, api_version: ApiVersion
):
    expected = (
        f"/data/{context.value}/{agency}/*/*/*"
        "?attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(context, agency)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_add_default_agency_if_required_before_2_0_0(
    context: DataContext, res: str, api_version: ApiVersion
):
    expected = f"/data/{res}"

    q = DataQuery(context, resource_id=res)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_add_default_agency_if_required_since_2_0_0(
    context: DataContext, res: str, api_version: ApiVersion
):
    expected = f"/data/{context.value}/*/{res}"

    q = DataQuery(context, resource_id=res)
    url = q.get_url(api_version, True)

    assert url == expected
