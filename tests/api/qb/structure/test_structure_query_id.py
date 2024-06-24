from typing import List

import pytest

from pysdmx.api.qb.structure import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import ClientError


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
def mult_res():
    return ["CBS", "LBS"]


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def detail():
    return StructureDetail.FULL


@pytest.fixture
def refs():
    return StructureReference.NONE


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V1_3_0)
)
def test_url_multiple_ids_until_1_2_0(
    typ: StructureType,
    agency: str,
    mult_res: List[str],
    api_version: ApiVersion,
):
    with pytest.raises(ClientError):
        q = StructureQuery(typ, agency, mult_res)
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_url_multiple_ids_until_1_5_0(
    typ: StructureType,
    agency: str,
    mult_res: List[str],
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{'+'.join(mult_res)}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, mult_res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_ids_since_2_0_0(
    typ: StructureType,
    agency: str,
    mult_res: List[str],
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{','.join(mult_res)}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, mult_res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_url_default_id_before_2_0_0(
    typ: StructureType,
    agency: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/all/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, version=version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_id_since_2_0_0(
    typ: StructureType,
    agency: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/*/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, version=version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_single_id_before_2_0_0(
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
def test_url_single_id_since_2_0_0(
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
