import pytest

from pysdmx.api.qb.schema import (
    SchemaContext,
    SchemaQuery,
)
from pysdmx.api.qb.util import ApiVersion, REST_ALL
from pysdmx.errors import ClientError


@pytest.fixture()
def context():
    return SchemaContext.DATAFLOW


@pytest.fixture()
def agency():
    return "BIS"


@pytest.fixture()
def res():
    return "CBS"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_latest_version_before_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/schema/{context.value}/{agency}/{res}/latest?explicit=false"

    q = SchemaQuery(context, agency, res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_latest_version_since_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/schema/{context.value}/{agency}/{res}/~"

    q = SchemaQuery(context, agency, res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_short_url_latest_version_before_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/schema/{context.value}/{agency}/{res}"

    q = SchemaQuery(context, agency, res)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_short_url_latest_version_since_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/schema/{context.value}/{agency}/{res}"

    q = SchemaQuery(context, agency, res)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize("api_version", ApiVersion)
def test_all_not_allowed(
    context: SchemaContext,
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    q = SchemaQuery(context, agency, res, REST_ALL)

    with pytest.raises(ClientError):
        q.get_url(api_version, True)
