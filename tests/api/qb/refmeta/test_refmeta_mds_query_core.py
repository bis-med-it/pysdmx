import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadatasetQuery, RefMetaDetail
from pysdmx.api.qb.util import ApiVersion, REST_ALL, REST_LATEST
from pysdmx.errors import ClientError


@pytest.fixture()
def provider():
    return "5B0"


@pytest.fixture()
def res():
    return "mds_id"


@pytest.fixture()
def version():
    return "1.0"


@pytest.fixture()
def detail():
    return RefMetaDetail.ALL_STUBS


def test_expected_defaults():
    q = RefMetaByMetadatasetQuery()

    assert q.provider_id == REST_ALL
    assert q.metadataset_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.detail == RefMetaDetail.FULL


def test_validate_ok():
    q = RefMetaByMetadatasetQuery()

    q.validate()

    assert q.provider_id == REST_ALL
    assert q.metadataset_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.detail == RefMetaDetail.FULL


def test_validate_nok():
    q = RefMetaByMetadatasetQuery(provider_id=42)

    with pytest.raises(ClientError):
        q.validate()


def test_rest_url_for_metadata_query(
    provider: str,
    res: str,
    version: str,
    detail: RefMetaDetail,
):
    expected = (
        f"/metadata/metadataset/{provider}/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByMetadatasetQuery(provider, res, version, detail)
    url = q.get_url(ApiVersion.V2_0_0)

    assert url == expected
