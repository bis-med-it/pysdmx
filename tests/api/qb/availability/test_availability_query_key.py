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
    return "BIS"


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def key():
    return "A.EUR.CHF"


@pytest.fixture
def keys():
    return ["A.EUR.CHF", "A.JPY.CHF"]


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_availability_url_multiple_keys_before_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    keys: List[str],
    api_version: ApiVersion,
):
    q = AvailabilityQuery(context, agency, res, version, keys)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_multiple_keys_since_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    keys: List[str],
    api_version: ApiVersion,
):
    expected = (
        f"/availability/{context.value}/{agency}/{res}/{version}/"
        f"{','.join(keys)}/*?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, version, keys)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_multiple_keys_since_2_0_0_short(
    context: DataContext,
    keys: List[str],
    api_version: ApiVersion,
):
    expected = f"/availability/{context.value}/*/*/*/{','.join(keys)}"

    q = AvailabilityQuery(context, key=keys)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_availability_url_default_key_before_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = (
        f"/availableconstraint/{agency},{res},{version}/all/all"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, version)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_availability_url_default_key_since_2_0_0(
    context: DataContext, agency, res, version, api_version: ApiVersion
):
    expected = (
        f"/availability/{context.value}/{agency}/{res}/{version}/*/*"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, version)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_availability_url_single_key_before_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    key: str,
    api_version: ApiVersion,
):
    expected = (
        f"/availableconstraint/{agency},{res},{version}/{key}/all"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, version, key)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_single_key_since_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    key: str,
    api_version: ApiVersion,
):
    expected = (
        f"/availability/{context.value}/{agency}/{res}/{version}/{key}/*"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, version, key)
    url = q.get_url(api_version)

    assert url == expected
