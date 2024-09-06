import random
from typing import List

import pytest

from pysdmx.api.qb.data import DataContext, DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


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


@pytest.fixture()
def v1u():
    return random.choice([v for v in ApiVersion if v < ApiVersion.V2_0_0])


@pytest.fixture()
def v2u():
    return random.choice([v for v in ApiVersion if v >= ApiVersion.V2_0_0])


def test_url_multiple_agencies_before_2_0_0(
    context: DataContext, agencies: List[str], v1u: ApiVersion
):
    q = DataQuery(context, agencies)

    with pytest.raises(Invalid):
        q.get_url(api_version)


def test_url_multiple_agencies_since_2_0_0(
    context: DataContext, agencies: List[str], v2u: ApiVersion
):
    expected = (
        f"/data/{context.value}/{','.join(agencies)}/*/*/*"
        f"?attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(context, agencies)
    url = q.get_url(v2u)

    assert url == expected


def test_url_multiple_agencies_since_2_0_0_short(
    agencies: List[str], v2u: ApiVersion
):
    expected = f"/data/*/{','.join(agencies)}"

    q = DataQuery(agency_id=agencies)
    url = q.get_url(v2u, True)

    assert url == expected


def test_url_default_agency_before_2_0_0(
    context: DataContext, res: str, v1u: ApiVersion
):
    expected = f"/data/all,{res},latest/all?detail=full&includeHistory=false"

    q = DataQuery(context, resource_id=res)
    url = q.get_url(v1u)

    assert url == expected


def test_url_default_agency_since_2_0_0(context: DataContext, v2u: ApiVersion):
    expected = (
        f"/data/{context.value}/*/*/*/*"
        "?attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(context)
    url = q.get_url(v2u)

    assert url == expected


def test_url_single_agency_before_2_0_0(
    context: DataContext, agency: str, res: str, v1u: ApiVersion
):
    expected = (
        f"/data/{agency},{res},latest/all?detail=full&includeHistory=false"
    )

    q = DataQuery(context, agency, res)
    url = q.get_url(v1u)

    assert url == expected


def test_url_single_agency_since_2_0_0(
    context: DataContext, agency: str, v2u: ApiVersion
):
    expected = (
        f"/data/{context.value}/{agency}/*/*/*"
        "?attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(context, agency)
    url = q.get_url(v2u)

    assert url == expected


def test_url_add_default_agency_if_required_before_2_0_0(
    context: DataContext, res: str, v1u: ApiVersion
):
    expected = f"/data/{res}"

    q = DataQuery(context, resource_id=res)
    url = q.get_url(v1u, True)

    assert url == expected


def test_url_add_default_agency_if_required_since_2_0_0(
    context: DataContext, res: str, v2u: ApiVersion
):
    expected = f"/data/{context.value}/*/{res}"

    q = DataQuery(context, resource_id=res)
    url = q.get_url(v2u, True)

    assert url == expected
