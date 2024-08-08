from typing import List

import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadataflowQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture()
def agency():
    return "SDMX"


@pytest.fixture()
def agencies():
    return ["BIS", "SDMX"]


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
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_multiple_agencies(
    agencies: List[str],
    res: str,
    version: str,
    provider: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/{','.join(agencies)}/{res}/{version}"
        f"/{provider}?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(agencies, res, version, provider, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_agency(
    res: str,
    version: str,
    provider: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/metadataflow/*/{res}/{version}/{provider}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(
        resource_id=res, version=version, provider_id=provider, detail=detail
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_agency(
    agency: str,
    version: str,
    provider: str,
    res: str,
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
def test_url_omit_default_agency(
    api_version: ApiVersion,
):
    expected = "/metadata/metadataflow"

    q = RefMetaByMetadataflowQuery()
    url = q.get_url(api_version, True)

    assert url == expected
