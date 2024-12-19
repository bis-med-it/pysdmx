import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadataflowQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion

details = [RefMetaDetail.FULL, RefMetaDetail.ALL_STUBS]


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


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("detail", details)
def test_url_details(
    agency: str,
    res: str,
    version: str,
    provider: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{res}/{version}/{provider}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(agency, res, version, provider, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_details(
    agency: str,
    res: str,
    version: str,
    provider: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataflow/{agency}/{res}/{version}/{provider}"

    q = RefMetaByMetadataflowQuery(agency, res, version, provider)
    url = q.get_url(api_version, True)

    assert url == expected
