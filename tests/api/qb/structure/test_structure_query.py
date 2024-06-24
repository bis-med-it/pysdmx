from pysdmx.api.qb.structure import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.qb.util import REST_ALL, REST_LATEST


def test_expected_defaults():
    q = StructureQuery()

    assert q.artefact_type.value == REST_ALL
    assert q.agency_id == REST_ALL
    assert q.resource_id == REST_ALL
    assert q.version == REST_LATEST
    assert q.item_id == REST_ALL
    assert q.detail == StructureDetail.FULL
    assert q.references == StructureReference.NONE
