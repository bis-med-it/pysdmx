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
def versions():
    return ["1.0", "2.0"]


@pytest.fixture
def key():
    return "A.EUR.CHF"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_availability_url_multiple_versions_before_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    versions: List[str],
    api_version: ApiVersion,
):
    q = AvailabilityQuery(context, agency, res, versions)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_multiple_versions_since_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    versions: List[str],
    api_version: ApiVersion,
):
    expected = (
        f"/availability/{context.value}/{agency}/{res}/{','.join(versions)}"
        f"/*/*?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, versions)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_multiple_versions_since_2_0_0_short(
    context: DataContext,
    versions: List[str],
    api_version: ApiVersion,
):
    expected = f"/availability/{context.value}/*/*/{','.join(versions)}"

    q = AvailabilityQuery(context, version=versions)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_availability_url_default_version_before_2_0_0(
    context: DataContext, agency: str, res: str, api_version: ApiVersion
):
    expected = (
        f"/availableconstraint/{agency},{res},latest/all/all"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_availability_url_default_version_since_2_0_0(
    context: DataContext, agency, res, api_version: ApiVersion
):
    expected = (
        f"/availability/{context.value}/{agency}/{res}/*/*/*"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_availability_url_single_version_before_2_0_0(
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
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_availability_url_translate_latest_before_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = (
        f"/availableconstraint/{agency},{res},latest/all/all"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, "~")
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_single_version_since_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
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
def test_availability_url_add_default_version_if_required_before_2_0_0(
    context: DataContext, res: str, key: str, api_version: ApiVersion
):
    expected = f"/availableconstraint/{res}/{key}"

    q = AvailabilityQuery(context, resource_id=res, key=key)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_add_default_version_if_required_since_2_0_0(
    context: DataContext, key: str, api_version: ApiVersion
):
    expected = f"/availability/{context.value}/*/*/*/{key}"

    q = AvailabilityQuery(context, key=key)
    url = q.get_url(api_version, True)

    assert url == expected
