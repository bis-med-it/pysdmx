from typing import List

import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadataflowQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion


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
def provider():
    return "5B0"


@pytest.fixture()
def versions():
    return ["1.0", "2.0"]


@pytest.fixture()
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_versions(
    agency: str,
    res: str,
    versions: List[str],
    provider: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{res}/{','.join(versions)}"
        f"/{provider}?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(agency, res, versions, provider, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_default_version(
    agency: str,
    res: str,
    provider: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{res}/~/{provider}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(
        agency, res, provider_id=provider, detail=detail
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_version(
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
def test_url_omit_default_version(
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataflow/{agency}/{res}"

    q = RefMetaByMetadataflowQuery(agency, res)
    url = q.get_url(api_version, True)

    assert url == expected
