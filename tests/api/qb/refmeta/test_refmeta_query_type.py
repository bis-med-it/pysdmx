from typing import List

import pytest
from tests.api.qb.structure.test_common import (
    types_2_0_0_all,
    types_2_0_0_deprecated,
)

from pysdmx.api.qb.refmeta import RefMetaByStructureQuery, RefMetaDetail
from pysdmx.api.qb.structure import StructureType
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import ClientError


@pytest.fixture()
def typ():
    return StructureType.CATEGORISATION


@pytest.fixture()
def agency():
    return "SDMX"


@pytest.fixture()
def res():
    return "CORE"


@pytest.fixture()
def version():
    return "1.0"


@pytest.fixture()
def detail():
    return RefMetaDetail.FULL


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_type(
    agency: str,
    res: str,
    version: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/metadata/structure/*/{agency}/{res}/{version}"
        f"?detail={detail.value}"
    )

    q = RefMetaByStructureQuery(
        agency_id=agency,
        resource_id=res,
        version=version,
        detail=detail,
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_no_metadata_queries_before_2_0_0(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    q = RefMetaByStructureQuery(typ, agency, res, version, detail)
    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_type(
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
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
@pytest.mark.parametrize("atype", types_2_0_0_deprecated)
def test_url_v2_0_0_deprecated(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: RefMetaDetail,
    api_version: ApiVersion,
):
    q = RefMetaByStructureQuery(atype, agency, res, version, detail)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_type(
    api_version: ApiVersion,
):
    expected = "/metadata/structure"

    q = RefMetaByStructureQuery()
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_add_defaults_if_required(version: str, api_version: ApiVersion):
    expected = f"/metadata/structure/*/*/*/{version}"

    q = RefMetaByStructureQuery(version=version)
    url = q.get_url(api_version, True)

    assert url == expected
