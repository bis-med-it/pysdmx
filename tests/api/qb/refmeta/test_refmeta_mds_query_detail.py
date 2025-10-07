import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadatasetQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion

details = [RefMetaDetail.FULL, RefMetaDetail.ALL_STUBS]


@pytest.fixture
def provider():
    return "BIS"


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def version():
    return "1.0"


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("detail", details)
def test_url_details(
    provider: str,
    res: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataset/{provider}/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadatasetQuery(provider, res, version, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_short_url_details(
    provider: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    d = RefMetaDetail.ALL_STUBS
    expected = (
        f"/metadata/metadataset/{provider}/{res}/{version}"
        f"?detail={d.value}"
    )

    q = RefMetaByMetadatasetQuery(provider, res, version, d)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_details(
    provider: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataset/{provider}/{res}/{version}"

    q = RefMetaByMetadatasetQuery(provider, res, version)
    url = q.get_url(api_version, True)

    assert url == expected
