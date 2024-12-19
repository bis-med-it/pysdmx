from typing import List

import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadatasetQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def provider():
    return "5B0"


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def versions():
    return ["1.0", "2.0"]


@pytest.fixture
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_versions(
    provider: str,
    res: str,
    versions: List[str],
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataset/{provider}/{res}/{','.join(versions)}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadatasetQuery(provider, res, versions, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_default_version(
    provider: str,
    res: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataset/{provider}/{res}/~?detail={detail.value}"
    )

    q = RefMetaByMetadatasetQuery(provider, res, detail=detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_version(
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
def test_url_omit_default_version(
    provider: str,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataset/{provider}/{res}"

    q = RefMetaByMetadatasetQuery(provider, res)
    url = q.get_url(api_version, True)

    assert url == expected
