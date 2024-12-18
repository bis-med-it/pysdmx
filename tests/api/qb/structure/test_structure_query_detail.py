import pytest

from pysdmx.api.qb.structure import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


details_initial = [
    StructureDetail.FULL,
    StructureDetail.ALL_STUBS,
    StructureDetail.REFERENCE_STUBS,
]


details_1_3_0 = [
    StructureDetail.REFERENCE_PARTIAL,
    StructureDetail.REFERENCE_COMPLETE_STUBS,
    StructureDetail.ALL_COMPLETE_STUBS,
]


details_2_0_0 = [StructureDetail.RAW]


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
def version():
    return "1.0"


@pytest.fixture()
def refs():
    return StructureReference.ALL


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("detail", details_initial)
def test_url_core_details_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    detail: StructureDetail,
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
@pytest.mark.parametrize("detail", details_initial)
def test_url_core_details_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    detail: StructureDetail,
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
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("detail", details_1_3_0)
def test_url_1_3_0_details_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    detail: StructureDetail,
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
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
@pytest.mark.parametrize("detail", details_1_3_0)
def test_url_1_3_0_details_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    detail: StructureDetail,
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
@pytest.mark.parametrize("detail", details_2_0_0)
def test_url_2_0_0_details_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    detail: StructureDetail,
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
@pytest.mark.parametrize("detail", details_2_0_0)
def test_url_2_0_0_details_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    detail: StructureDetail,
    api_version: ApiVersion,
):
    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V1_3_0)
)
@pytest.mark.parametrize("detail", details_1_3_0)
def test_url_1_3_0_details_before_1_3_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    detail: StructureDetail,
    api_version: ApiVersion,
):
    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_omit_default_details_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    api_version: ApiVersion,
):
    detail = StructureDetail.FULL
    expected = f"/{typ.value}/{agency}/{res}/{version}?references={refs.value}"

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_details_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    refs: StructureReference,
    api_version: ApiVersion,
):
    detail = StructureDetail.FULL
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{version}"
        f"?references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version, True)

    assert url == expected
