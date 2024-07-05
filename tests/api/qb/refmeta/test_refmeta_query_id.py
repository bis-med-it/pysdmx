from typing import List

import pytest


from pysdmx.api.qb.refmeta import RefMetaByStructureQuery, RefMetaDetail
from pysdmx.api.qb.structure import StructureType
from pysdmx.api.qb.util import ApiVersion


@pytest.fixture()
def typ():
    return StructureType.DATAFLOW


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
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_ids(
    typ: StructureType,
    agency: str,
    mult_res: List[str],
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/{typ.value}/{agency}/{','.join(mult_res)}"
        f"/{version}?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(typ, agency, mult_res, version, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_id(
    typ: StructureType,
    agency: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/{typ.value}/{agency}/*/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(typ, agency, version=version, detail=detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_id(
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

    q = RefMetaByStructureQuery(typ, agency, res, version, detail)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_id(
    typ: StructureType,
    agency: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/structure/{typ.value}/{agency}"

    q = RefMetaByStructureQuery(typ, agency)
    url = q.get_url(api_version, True)

    assert url == expected
