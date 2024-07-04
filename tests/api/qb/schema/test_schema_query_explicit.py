import pytest

from pysdmx.api.qb.schema import (
    SchemaContext,
    SchemaQuery,
)
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import ClientError


@pytest.fixture()
def context():
    return SchemaContext.DATA_STRUCTURE


@pytest.fixture()
def agency():
    return "BIS"


@pytest.fixture()
def res():
    return "CBS"


@pytest.fixture()
def version():
    return "1.0"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_default_explicit(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}?explicit=false"
    )

    q = SchemaQuery(context, agency, res, version)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_false_explicit(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}?explicit=false"
    )

    q = SchemaQuery(context, agency, res, version, explicit=False)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_true_explicit(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = (
        f"/schema/{context.value}/{agency}/{res}/{version}?explicit=true"
    )

    q = SchemaQuery(context, agency, res, version, explicit=True)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_short_url_default_explicit(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = f"/schema/{context.value}/{agency}/{res}/{version}"

    q = SchemaQuery(context, agency, res, version)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v > ApiVersion.V2_0_0)
)
def test_explicit_not_allowed(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    q = SchemaQuery(context, agency, res, version, explicit=True)

    with pytest.raises(ClientError):
        q.get_url(api_version)
