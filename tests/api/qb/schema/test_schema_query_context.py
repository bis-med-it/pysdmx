import pytest

from pysdmx.api.qb.schema import (
    SchemaContext,
    SchemaQuery,
)
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import ClientError

context_initial = [
    SchemaContext.DATA_STRUCTURE,
    SchemaContext.DATAFLOW,
    SchemaContext.METADATA_STRUCTURE,
    SchemaContext.METADATA_FLOW,
    SchemaContext.PROVISION_AGREEMENT,
]

context_2_0_0 = [SchemaContext.METADATA_PROVISION_AGREEMENT]
all_context = context_initial.copy()
all_context.extend(context_2_0_0)


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
@pytest.mark.parametrize("context", context_initial)
def test_url_core_context_before_2_0_0(
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
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("context", context_initial)
def test_url_core_context_since_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = f"/schema/{context.value}/{agency}/{res}/{version}"

    q = SchemaQuery(context, agency, res, version)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("context", context_2_0_0)
def test_url_2_0_0_context_before_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    q = SchemaQuery(context, agency, res, version)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("context", context_2_0_0)
def test_url_2_0_0_context_since_2_0_0(
    context: SchemaContext,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = f"/schema/{context.value}/{agency}/{res}/{version}"

    q = SchemaQuery(context, agency, res, version)
    url = q.get_url(api_version)

    assert url == expected
