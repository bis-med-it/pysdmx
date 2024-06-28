from typing import List

import pytest
from tests.api.qb.structure.test_common import (
    types_1_3_0,
    types_1_5_0,
    types_2_0_0_added,
    types_2_0_0_all,
    types_2_0_0_deprecated,
    types_initial,
)

from pysdmx.api.qb.structure import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import ClientError


@pytest.fixture()
def typ():
    return StructureType.CATEGORISATION


@pytest.fixture()
def typs():
    return [StructureType.CATEGORISATION, StructureType.METADATAFLOW]


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
    return StructureDetail.FULL


@pytest.fixture()
def refs():
    return StructureReference.NONE


@pytest.mark.parametrize("api_version", ApiVersion)
def test_url_multiple_types_until_1_2_0(
    typs: List[StructureType], agency: str, res: str, api_version: ApiVersion
):
    q = StructureQuery(typs, agency, res)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_url_default_type_before_2_0_0(
    agency: str,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        agency_id=agency,
        resource_id=res,
        version=version,
        detail=detail,
        references=refs,
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_type_since_2_0_0(
    agency: str,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/*/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        agency_id=agency,
        resource_id=res,
        version=version,
        detail=detail,
        references=refs,
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_single_type_before_2_0_0(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_single_type_since_2_0_0(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("atype", types_initial)
def test_url_initial_type_before_2_0_0(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    exp1 = (
        f"/{atype.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )
    exp2 = (
        f"/{atype.value}/{agency}/{res}/{version}/all"
        f"?detail={detail.value}&references={refs.value}"
    )
    expected = [exp1, exp2]
    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url in expected


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
@pytest.mark.parametrize("atype", types_1_3_0)
def test_url_v1_3_0_type_before_2_0_0(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{atype.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )
    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url in expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v == ApiVersion.V1_5_0),
)
@pytest.mark.parametrize("atype", types_1_5_0)
def test_url_v1_5_0_type_before_2_0_0(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{atype.value}/{agency}/{res}/{version}/all"
        f"?detail={detail.value}&references={refs.value}"
    )
    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url in expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V1_3_0),
)
@pytest.mark.parametrize("atype", types_1_3_0)
def test_url_v1_3_0_type_before_1_3_0(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V1_5_0),
)
@pytest.mark.parametrize("atype", types_1_5_0)
def test_url_v1_5_0_type_before_1_5_0(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )

    with pytest.raises(ClientError):
        q.get_url(api_version)


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
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
@pytest.mark.parametrize("atype", types_2_0_0_added)
def test_url_v2_0_0_added_since_2_0_0(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    exp1 = (
        f"/structure/{atype.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )
    exp2 = (
        f"/structure/{atype.value}/{agency}/{res}/{version}/*"
        f"?detail={detail.value}&references={refs.value}"
    )
    expected = [exp1, exp2]

    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url in expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
@pytest.mark.parametrize("atype", types_2_0_0_added)
def test_url_v2_0_0_added_before_2_0_0(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("atype", types_2_0_0_all)
def test_url_v2_0_0_type(
    atype: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    exp1 = (
        f"/structure/{atype.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )
    exp2 = (
        f"/structure/{atype.value}/{agency}/{res}/{version}/*"
        f"?detail={detail.value}&references={refs.value}"
    )
    expected = [exp1, exp2]
    q = StructureQuery(
        atype, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url in expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_omit_default_type_before_2_0_0(
    api_version: ApiVersion,
):
    expected = "/structure"

    q = StructureQuery()
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_type_since_2_0_0(
    api_version: ApiVersion,
):
    expected = "/structure"

    q = StructureQuery()
    url = q.get_url(api_version, True)

    assert url == expected
