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
    return StructureType.METADATA_STRUCTURE


@pytest.fixture
def agency():
    return "SDMX"


@pytest.fixture
def agencies():
    return ["BIS", "SDMX"]


@pytest.fixture
def res():
    return "REF_META"


@pytest.fixture
def version():
    return "1.0.0"


@pytest.fixture
def detail():
    return StructureDetail.FULL


@pytest.fixture
def refs():
    return StructureReference.NONE


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V1_3_0)
)
def test_url_multiple_agencies_until_1_2_0(
    typ: StructureType, agencies: List[str], res: str, api_version: ApiVersion
):
    with pytest.raises(ClientError):
        q = StructureQuery(typ, agencies, res)
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_url_multiple_agencies_until_1_5_0(
    typ: StructureType,
    agencies: List[str],
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{'+'.join(agencies)}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agencies, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multiple_agencies_since_2_0_0(
    typ: StructureType,
    agencies: List[str],
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{','.join(agencies)}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agencies, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V2_0_0),
)
def test_url_default_agency_before_2_0_0(
    typ: StructureType,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/all/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, resource_id=res, version=version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
def test_url_default_agency_since_2_0_0(
    typ: StructureType,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/*/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, resource_id=res, version=version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_single_agency_before_2_0_0(
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
def test_url_single_agency_since_2_0_0(
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
