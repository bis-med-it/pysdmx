import pytest

from pysdmx.api.qb.refmeta import RefMetaByStructureQuery, RefMetaDetail
from pysdmx.api.qb.structure import StructureType
from pysdmx.api.qb.util import ApiVersion

details = [RefMetaDetail.FULL, RefMetaDetail.ALL_STUBS]


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


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("detail", details)
def test_url_details(
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
def test_url_omit_default_details(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    api_version: ApiVersion,
):
    expected = f"/metadata/structure/{typ.value}/{agency}/{res}/{version}"

    q = RefMetaByStructureQuery(typ, agency, res, version)
    url = q.get_url(api_version, True)

    assert url == expected
