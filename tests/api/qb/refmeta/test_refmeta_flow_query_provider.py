from typing import List

import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadataflowQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture()
def agency():
    return "SDMX"


@pytest.fixture()
def res():
    return "REF_META"


@pytest.fixture()
def version():
    return "1.0.0"


@pytest.fixture()
def provider():
    return "5B0"


@pytest.fixture()
def providers():
    return ["5B0", "4F0"]


@pytest.fixture()
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_multiple_providers(
    agency: str,
    res: str,
    version: str,
    providers: List[str],
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{res}/{version}"
        f"/{','.join(providers)}?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(agency, res, version, providers, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_provider(
    agency: str,
    res: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{res}/{version}/*"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(agency, res, version, detail=detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_provider(
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
def test_url_omit_default_provider(
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataflow/{agency}/{res}/{version}"

    q = RefMetaByMetadataflowQuery(agency, res, version)
    url = q.get_url(api_version, True)

    assert url == expected
