from typing import List

import pytest

from pysdmx.api.qb.refmeta import RefMetaByStructureQuery, RefMetaDetail
from pysdmx.api.qb.structure import StructureType
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture
def typ():
    return StructureType.DATA_STRUCTURE


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
def versions():
    return ["1.0", "2.0"]


@pytest.fixture
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_versions(
    typ: StructureType,
    agency: str,
    res: str,
    versions: List[str],
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/{typ.value}/{agency}/{res}/{','.join(versions)}"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(typ, agency, res, versions, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_default_version(
    typ: StructureType,
    agency: str,
    res: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/{typ.value}/{agency}/{res}/~"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(typ, agency, res, detail=detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_version(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(typ, agency, res, version, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_version(
    typ: StructureType,
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/structure/{typ.value}/{agency}/{res}"

    q = RefMetaByStructureQuery(typ, agency, res)
    url = q.get_url(api_version, True)

    assert url == expected
