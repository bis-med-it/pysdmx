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
def mult_res():
    return ["CBS", "LBS"]


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_ids(
    provider: str,
    mult_res: List[str],
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataset/{provider}/{','.join(mult_res)}"
        f"/{version}?detail={detail.value}"
    )

    q = RefMetaByMetadatasetQuery(provider, mult_res, version, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_id(
    provider: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataset/{provider}/*/{version}?detail={detail.value}"
    )

    q = RefMetaByMetadatasetQuery(provider, version=version, detail=detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_id(
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
def test_url_omit_default_id(
    provider: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataset/{provider}"

    q = RefMetaByMetadatasetQuery(provider)
    url = q.get_url(api_version, True)

    assert url == expected
