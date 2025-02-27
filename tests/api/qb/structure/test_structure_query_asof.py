from datetime import datetime, timezone

import pytest

from pysdmx.api.qb.structure import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture
def typ():
    return StructureType.DATAFLOW


@pytest.fixture
def agency():
    return "BIS"


@pytest.fixture
def res():
    return "CBS"


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def detail():
    return StructureDetail.ALL_STUBS


@pytest.fixture
def references():
    return StructureReference.ALL


@pytest.fixture
def as_of():
    return datetime(2025, 1, 1, 12, 42, 21, tzinfo=timezone.utc)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_url_asof_since_2_2_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    references: StructureReference,
    detail: StructureDetail,
    as_of: datetime,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={references.value}"
        f"&asOf=2025-01-01T12:42:21+00:00"
    )

    q = StructureQuery(
        typ,
        agency,
        res,
        version,
        detail=detail,
        references=references,
        as_of=as_of,
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_asof_since_2_2_0(
    as_of: datetime,
    api_version: ApiVersion,
):
    expected = "/structure?asOf=2025-01-01T12:42:21+00:00"

    q = StructureQuery(as_of=as_of)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_2_0)
)
def test_short_url_asof_and_detail_since_2_2_0(
    detail: StructureDetail,
    as_of: datetime,
    api_version: ApiVersion,
):
    expected = (
        f"/structure?detail={detail.value}&asOf=2025-01-01T12:42:21+00:00"
    )

    q = StructureQuery(detail=detail, as_of=as_of)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_2_0)
)
def test_url_as_of_before_2_2_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    references: StructureReference,
    detail: StructureDetail,
    as_of: datetime,
    api_version: ApiVersion,
):
    q = StructureQuery(
        typ,
        agency,
        res,
        version,
        detail=detail,
        references=references,
        as_of=as_of,
    )

    with pytest.raises(Invalid):
        q.get_url(api_version)
