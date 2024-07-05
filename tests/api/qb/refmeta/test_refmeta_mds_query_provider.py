from typing import List

import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadatasetQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture()
def provider():
    return "5B0"


@pytest.fixture()
def providers():
    return ["5B0", "4F0"]


@pytest.fixture()
def res():
    return "REF_META"


@pytest.fixture()
def version():
    return "1.0.0"


@pytest.fixture()
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_multiple_agencies(
    providers: List[str],
    res: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataset/{','.join(providers)}/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadatasetQuery(providers, res, version, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_provider(
    res: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataset/*/{res}/{version}?detail={detail.value}"

    q = RefMetaByMetadatasetQuery(
        metadataset_id=res, version=version, detail=detail
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_provider(
    provider: str,
    version,
    res: str,
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
def test_url_omit_default_provider(
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataset"

    q = RefMetaByMetadatasetQuery()
    url = q.get_url(api_version, True)

    assert url == expected
