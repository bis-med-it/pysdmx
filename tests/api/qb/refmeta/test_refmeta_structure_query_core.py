import pytest

from pysdmx.api.qb.refmeta import RefMetaByStructureQuery, RefMetaDetail
from pysdmx.api.qb.structure import StructureType
from pysdmx.api.qb.util import ApiVersion, REST_ALL, REST_LATEST
from pysdmx.errors import Invalid


@pytest.fixture()
def typ():
    return StructureType.DATA_STRUCTURE


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
def detail():
    return RefMetaDetail.ALL_STUBS


def test_expected_defaults():
    q = RefMetaByStructureQuery()

    assert q.artefact_type.value == REST_ALL
    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.detail == RefMetaDetail.FULL


def test_validate_ok():
    q = RefMetaByStructureQuery()

    q.validate()

    assert q.artefact_type.value == REST_ALL
    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.detail == RefMetaDetail.FULL


def test_validate_nok():
    q = RefMetaByStructureQuery(artefact_type=42)

    with pytest.raises(Invalid):
        q.validate()


def test_rest_url_for_metadata_query(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    detail: RefMetaDetail,
):
    expected = (
        f"/metadata/structure/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(typ, agency, res, version, detail)
    url = q.get_url(ApiVersion.V2_0_0)

    assert url == expected
