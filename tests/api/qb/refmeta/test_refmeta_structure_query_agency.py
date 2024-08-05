from typing import List

import pytest

from pysdmx.api.qb.refmeta import RefMetaByStructureQuery, RefMetaDetail
from pysdmx.api.qb.structure import StructureType
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture()
def typ():
    return StructureType.METADATA_STRUCTURE


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
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_multiple_agencies(
    typ: StructureType,
    agencies: List[str],
    res: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/{typ.value}/{','.join(agencies)}/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(typ, agencies, res, version, detail=detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_agency(
    typ: StructureType,
    res: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/{typ.value}/*/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(
        typ, resource_id=res, version=version, detail=detail
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_agency(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(typ, agency, res, version, detail=detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_agency(
    typ: StructureType,
    api_version: ApiVersion,
):
    expected = f"/metadata/structure/{typ.value}"

    q = RefMetaByStructureQuery(typ)
    url = q.get_url(api_version, True)

    assert url == expected
