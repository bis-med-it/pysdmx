import random
from typing import List

import pytest

from pysdmx.api.qb.availability import AvailabilityQuery
from pysdmx.api.qb.data import DataContext
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def context():
    return DataContext.DATAFLOW


@pytest.fixture
def agency():
    return "SDMX"


@pytest.fixture
def agencies():
    return ["BIS", "SDMX"]


@pytest.fixture
def res():
    return "REF_META"


@pytest.fixture
def v1u():
    return random.choice([v for v in ApiVersion if v < ApiVersion.V2_0_0])


@pytest.fixture
def v13u():
    return random.choice(
        [
            v
            for v in ApiVersion
            if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
        ]
    )


@pytest.fixture
def v2u():
    return random.choice([v for v in ApiVersion if v >= ApiVersion.V2_0_0])


def test_availability_url_multiple_agencies_before_2_0_0(
    context: DataContext, agencies: List[str], v13u: ApiVersion
):
    q = AvailabilityQuery(context, agencies)

    with pytest.raises(Invalid):
        q.get_url(v13u)


def test_availability_url_multiple_agencies_since_2_0_0(
    context: DataContext, agencies: List[str], v2u: ApiVersion
):
    expected = (
        f"/availability/{context.value}/{','.join(agencies)}/*/*/*/*"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agencies)
    url = q.get_url(v2u)

    assert url == expected


def test_availability_url_multiple_agencies_since_2_0_0_short(
    agencies: List[str], v2u: ApiVersion
):
    expected = f"/availability/*/{','.join(agencies)}"

    q = AvailabilityQuery(agency_id=agencies)
    url = q.get_url(v2u, True)

    assert url == expected


def test_availability_url_default_agency_before_2_0_0(
    context: DataContext, res: str, v13u: ApiVersion
):
    expected = (
        f"/availableconstraint/all,{res},latest/all/all?"
        "references=none&mode=exact"
    )

    q = AvailabilityQuery(context, resource_id=res)
    url = q.get_url(v13u)

    assert url == expected


def test_availability_url_default_agency_since_2_0_0(
    context: DataContext, v2u: ApiVersion
):
    expected = (
        f"/availability/{context.value}/*/*/*/*/*?references=none&mode=exact"
    )

    q = AvailabilityQuery(context)
    url = q.get_url(v2u)

    assert url == expected


def test_availability_url_single_agency_before_2_0_0(
    context: DataContext, agency: str, res: str, v1u: ApiVersion
):
    expected = (
        f"/availableconstraint/{agency},{res},latest/all/all"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res)
    url = q.get_url(v1u)

    assert url == expected


def test_availability_url_single_agency_since_2_0_0(
    context: DataContext, agency: str, v2u: ApiVersion
):
    expected = (
        f"/availability/{context.value}/{agency}/*/*/*/*"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency)
    url = q.get_url(v2u)

    assert url == expected


def test_availability_url_add_default_agency_if_required_before_2_0_0(
    context: DataContext, res: str, v1u: ApiVersion
):
    expected = f"/availableconstraint/{res}"

    q = AvailabilityQuery(context, resource_id=res)
    url = q.get_url(v1u, True)

    assert url == expected


def test_availability_url_add_default_agency_if_required_since_2_0_0(
    context: DataContext, res: str, v2u: ApiVersion
):
    expected = f"/availability/{context.value}/*/{res}"

    q = AvailabilityQuery(context, resource_id=res)
    url = q.get_url(v2u, True)

    assert url == expected
