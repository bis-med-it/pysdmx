import pytest

from pysdmx.api.qb.data import DataContext, DataQuery
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def agency():
    return "BIS"


@pytest.fixture
def res():
    return "CBS"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize(
    "context",
    (c for c in DataContext if c in [DataContext.DATAFLOW, DataContext.ALL]),
)
def test_url_df_context_before_2_0_0(
    context: DataContext,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/data/all,{res},latest/all?detail=full&includeHistory=false"

    q = DataQuery(context, resource_id=res)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize(
    "context",
    (
        c
        for c in DataContext
        if c in [DataContext.DATA_STRUCTURE, DataContext.PROVISION_AGREEMENT]
    ),
)
def test_url_non_df_context_before_2_0_0(
    context: DataContext,
    api_version: ApiVersion,
):
    q = DataQuery(context)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V2_0_0 and v < ApiVersion.V2_2_0
    ),
)
@pytest.mark.parametrize("context", DataContext)
def test_url_context_since_2_0_0(
    context: DataContext,
    api_version: ApiVersion,
):
    expected = (
        f"/data/{context.value}/*/*/*/*?attributes=dsd&measures=all"
        "&includeHistory=false"
    )

    q = DataQuery(context)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
@pytest.mark.parametrize("context", DataContext)
def test_url_context_since_2_2_0(
    context: DataContext,
    api_version: ApiVersion,
):
    expected = (
        f"/data/{context.value}/*/*/*/*?attributes=dsd&measures=all"
        "&includeHistory=false&offset=0"
    )

    q = DataQuery(context)
    url = q.get_url(api_version)

    assert url == expected


def test_wrong_context():
    q = DataQuery(42)

    with pytest.raises(Invalid):
        q.get_url(ApiVersion.V2_0_0)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_add_defaults_if_required_since_2_0_0(
    agency: str,
    api_version: ApiVersion,
):
    expected = f"/data/*/{agency}"

    q = DataQuery(agency_id=agency)
    url = q.get_url(api_version, True)

    assert url == expected
