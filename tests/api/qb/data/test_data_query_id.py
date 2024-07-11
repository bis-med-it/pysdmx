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
    return "BIS"


@pytest.fixture()
def res():
    return "CBS"


@pytest.fixture()
def mult_res():
    return ["CBS", "LBS"]


@pytest.fixture()
def version():
    return "1.0"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_multiple_resources_before_2_0_0(
    context: DataContext,
    agency: str,
    mult_res: List[str],
    api_version: ApiVersion,
):
    q = DataQuery(context, agency, mult_res)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_resources_since_2_0_0(
    context: DataContext,
    agency: str,
    mult_res: List[str],
    api_version: ApiVersion,
):
    expected = (
        f"/data/{context.value}/{agency}/{','.join(mult_res)}/*/*"
        f"?attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(context, agency, mult_res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_url_default_resource_before_2_0_0(
    context: DataContext, agency: str, api_version: ApiVersion
):
    expected = (
        f"/data/{agency},all,latest/all?detail=full&includeHistory=false"
    )

    q = DataQuery(context, agency)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_resource_since_2_0_0(
    context: DataContext, agency, api_version: ApiVersion
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
def test_url_single_resource_before_2_0_0(
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
def test_url_single_resource_since_2_0_0(
    context: DataContext, agency: str, res: str, api_version: ApiVersion
):
    expected = (
        f"/data/{context.value}/{agency}/{res}/*/*"
        "?attributes=dsd&measures=all&includeHistory=false"
    )

    q = DataQuery(context, agency, res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_add_default_resource_if_required_before_2_0_0(
    context: DataContext, version: str, api_version: ApiVersion
):
    expected = f"/all,all,{version}"

    q = DataQuery(context, version=version)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_add_default_resource_if_required_since_2_0_0(
    context: DataContext, version: str, api_version: ApiVersion
):
    expected = f"/data/{context.value}/*/*/{version}"

    q = DataQuery(context, version=version)
    url = q.get_url(api_version, True)

    assert url == expected
