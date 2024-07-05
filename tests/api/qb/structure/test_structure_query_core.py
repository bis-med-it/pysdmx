import pytest

from pysdmx.api.qb.structure import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.qb.util import ApiVersion, REST_ALL, REST_LATEST
from pysdmx.errors import ClientError


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
    return StructureDetail.ALL_STUBS


@pytest.fixture()
def refs():
    return StructureReference.CHILDREN


def test_expected_defaults():
    q = StructureQuery()

    assert q.artefact_type.value == REST_ALL
    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.item_id == REST_ALL
    assert q.detail == StructureDetail.FULL
    assert q.references == StructureReference.NONE


def test_validate_ok():
    q = StructureQuery()

    q.validate()

    assert q.artefact_type.value == REST_ALL
    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.item_id == REST_ALL
    assert q.detail == StructureDetail.FULL
    assert q.references == StructureReference.NONE


def test_validate_nok():
    q = StructureQuery(artefact_type=42)

    with pytest.raises(ClientError):
        q.validate()


def test_rest_url_for_structure_query(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(ApiVersion.V1_5_0)

    assert url == expected
