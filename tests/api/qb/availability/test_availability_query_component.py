from typing import List

import pytest

from pysdmx.api.qb.availability import AvailabilityQuery
from pysdmx.api.qb.data import DataContext
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import ClientError


@pytest.fixture()
def context():
    return DataContext.DATAFLOW


@pytest.fixture()
def agency():
    return "BIS"


@pytest.fixture()
def res():
    return "CBS"


@pytest.fixture()
def version():
    return "1.0"


@pytest.fixture()
def key():
    return "A.EUR.CHF"


@pytest.fixture()
def component():
    return "REF_AREA"


@pytest.fixture()
def components():
    return ["REF_AREA", "ICP_ITEM"]


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_availability_url_multiple_components_before_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    key: str,
    components: List[str],
    api_version: ApiVersion,
):
    q = AvailabilityQuery(context, agency, res, version, key, components)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_multiple_components_since_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    key: str,
    components: List[str],
    api_version: ApiVersion,
):
    expected = (
        f"/availability/{context.value}/{agency}/{res}/{version}/{key}/"
        f"{','.join(components)}?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, version, key, components)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_multiple_components_since_2_0_0_short(
    context: DataContext,
    components: List[str],
    api_version: ApiVersion,
):
    expected = f"/availability/{context.value}/*/*/*/*/{','.join(components)}"

    q = AvailabilityQuery(context, component_id=components)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_availability_url_default_component_before_2_0_0(
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
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_availability_url_default_component_since_2_0_0(
    context: DataContext,
    agency,
    res,
    version,
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


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_availability_url_single_component_before_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    key: str,
    component: str,
    api_version: ApiVersion,
):
    expected = (
        f"/availableconstraint/{agency},{res},{version}/{key}/{component}"
        "?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, version, key, component)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_availability_url_single_component_since_2_0_0(
    context: DataContext,
    agency: str,
    res: str,
    version: str,
    key: str,
    component: str,
    api_version: ApiVersion,
):
    expected = (
        f"/availability/{context.value}/{agency}/{res}/{version}/{key}/"
        f"{component}?references=none&mode=exact"
    )

    q = AvailabilityQuery(context, agency, res, version, key, component)
    url = q.get_url(api_version)

    assert url == expected
