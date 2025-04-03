from datetime import datetime, timezone

import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadatasetQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def provider():
    return "BIS"


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def detail():
    return RefMetaDetail.FULL


@pytest.fixture
def as_of():
    return datetime(2025, 1, 1, 12, 42, 21, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_asof(
    provider: str,
    res: str,
    version: str,
    detail: RefMetaDetail,
    as_of: datetime,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataset/{provider}/{res}/{version}"
        f"?detail={detail.value}&asOf=2025-01-01T12:42:21+00:00"
    )

    q = RefMetaByMetadatasetQuery(provider, res, version, detail, as_of)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_asof(
    provider: str,
    as_of: datetime,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataset/{provider}?asOf=2025-01-01T12:42:21+00:00"
    )

    q = RefMetaByMetadatasetQuery(provider, as_of=as_of)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_asof_detail(
    provider: str,
    as_of: datetime,
    api_version: ApiVersion,
):
    d = RefMetaDetail.ALL_STUBS
    expected = (
        f"/metadata/metadataset/{provider}?"
        "detail=allstubs&asOf=2025-01-01T12:42:21+00:00"
    )

    q = RefMetaByMetadatasetQuery(provider, detail=d, as_of=as_of)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_2_0)
)
def test_url_asof_before_2_2_0(
    provider: str,
    res: str,
    version: str,
    as_of: datetime,
    api_version: ApiVersion,
):
    q = RefMetaByMetadatasetQuery(provider, res, version, as_of=as_of)
    with pytest.raises(Invalid):
        q.get_url(api_version, True)
