from datetime import datetime, timezone

import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadataflowQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


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
def provider():
    return "5B0"


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
    agency: str,
    res: str,
    version: str,
    provider: str,
    detail: RefMetaDetail,
    as_of: datetime,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{res}/{version}/{provider}"
        f"?detail={detail.value}&asOf=2025-01-01T12:42:21+00:00"
    )

    q = RefMetaByMetadataflowQuery(
        agency, res, version, provider, detail, as_of
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_asof(
    agency: str,
    res: str,
    as_of: datetime,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{res}"
        f"?asOf=2025-01-01T12:42:21+00:00"
    )

    q = RefMetaByMetadataflowQuery(agency, res, as_of=as_of)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_asof_detail(
    agency: str,
    res: str,
    as_of: datetime,
    api_version: ApiVersion,
):
    d = RefMetaDetail.ALL_STUBS
    expected = (
        f"/metadata/metadataflow/{agency}/{res}?"
        f"detail=allstubs&asOf=2025-01-01T12:42:21+00:00"
    )

    q = RefMetaByMetadataflowQuery(agency, res, detail=d, as_of=as_of)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_2_0)
)
def test_url_asof_before_2_2_0(
    agency: str,
    res: str,
    as_of: datetime,
    api_version: ApiVersion,
):
    q = RefMetaByMetadataflowQuery(agency, res, as_of=as_of)
    with pytest.raises(Invalid):
        q.get_url(api_version, True)
