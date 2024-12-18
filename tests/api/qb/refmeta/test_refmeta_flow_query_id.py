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
def mult_res():
    return ["CBS", "LBS"]


@pytest.fixture()
def version():
    return "1.0"


@pytest.fixture()
def provider():
    return "5B0"


@pytest.fixture()
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_ids(
    agency: str,
    mult_res: List[str],
    version: str,
    provider: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{','.join(mult_res)}"
        f"/{version}/{provider}?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(agency, mult_res, version, provider, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_id(
    agency: str,
    version: str,
    provider: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{agency}/*/{version}/{provider}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(
        agency, version=version, provider_id=provider, detail=detail
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_id(
    agency: str,
    version,
    res: str,
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
def test_url_omit_default_id(
    agency: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/metadataflow/{agency}"

    q = RefMetaByMetadataflowQuery(agency)
    url = q.get_url(api_version, True)

    assert url == expected
