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
def versions():
    return ["1.0", "2.0"]


@pytest.fixture()
def detail():
    return StructureDetail.FULL


@pytest.fixture()
def refs():
    return StructureReference.NONE


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V1_3_0)
)
def test_url_multiple_versions_until_1_2_0(
    typ: StructureType,
    agency: str,
    res: str,
    versions: List[str],
    api_version: ApiVersion,
):
    q = StructureQuery(typ, agency, res, versions)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_url_multiple_versions_until_1_5_0(
    typ: StructureType,
    agency: str,
    res: str,
    versions: List[str],
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{'+'.join(versions)}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, res, versions, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_versions_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    versions: List[str],
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{','.join(versions)}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, res, versions, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_url_default_version_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/latest"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(typ, agency, res, detail=detail, references=refs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_default_version_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/~"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(typ, agency, res, detail=detail, references=refs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_omit_default_version_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    version = "~"
    expected = f"/{typ.value}/{agency}/{res}"

    q = StructureQuery(typ, agency, res, version)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_version_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    api_version: ApiVersion,
):
    expected = f"/structure/{typ.value}/{agency}/{res}"

    q = StructureQuery(typ, agency, res)
    url = q.get_url(api_version, True)

    assert url == expected
