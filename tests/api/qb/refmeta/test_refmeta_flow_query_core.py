import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadataflowQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion, REST_ALL, REST_LATEST
from pysdmx.errors import ClientError


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
def detail():
    return RefMetaDetail.ALL_STUBS


def test_expected_defaults():
    q = RefMetaByMetadataflowQuery()

    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.provider_id == REST_ALL
    assert q.detail == RefMetaDetail.FULL


def test_validate_ok():
    q = RefMetaByMetadataflowQuery()

    q.validate()

    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.provider_id == REST_ALL
    assert q.detail == RefMetaDetail.FULL


def test_validate_nok():
    q = RefMetaByMetadataflowQuery(detail="wrong")

    with pytest.raises(ClientError):
        q.validate()


def test_rest_url_for_metadata_query(
    agency: str,
    res: str,
    version: str,
    provider: str,
    detail: RefMetaDetail,
):
    expected = (
        f"/metadata/metadataflow/{agency}/{res}/{version}/{provider}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadataflowQuery(agency, res, version, provider, detail)
    url = q.get_url(ApiVersion.V2_0_0)

    assert url == expected
