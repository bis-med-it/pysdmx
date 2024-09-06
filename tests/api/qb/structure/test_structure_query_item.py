from typing import List

import pytest

from pysdmx.api.qb.structure import (
    StructureDetail,
    StructureQuery,
    StructureReference,
    StructureType,
)
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import Invalid


@pytest.fixture()
def typ():
    return StructureType.CODELIST


@pytest.fixture()
def hcl():
    return StructureType.HIERARCHICAL_CODELIST


@pytest.fixture()
def hier():
    return StructureType.HIERARCHY


@pytest.fixture()
def agency():
    return "BIS"


@pytest.fixture()
def res():
    return "CL_FREQ"


@pytest.fixture()
def version():
    return "1.0"


@pytest.fixture()
def item():
    return "A"


@pytest.fixture()
def items():
    return ["A", "M"]


@pytest.fixture()
def detail():
    return StructureDetail.FULL


@pytest.fixture()
def refs():
    return StructureReference.NONE


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V1_1_0)
)
def test_url_item_query_until_1_0_2(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    item: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    q = StructureQuery(typ, agency, res, version, item, detail, refs)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V1_1_0)
)
def test_url_item_all_query_until_1_0_2(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
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
    "api_version",
    (v for v in ApiVersion if v > ApiVersion.V1_0_2 and v < ApiVersion.V2_0_0),
)
def test_url_item_query_since_1_1_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    item: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{version}/{item}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(typ, agency, res, version, item, detail, refs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v > ApiVersion.V1_0_2 and v < ApiVersion.V2_0_0),
)
def test_url_item_all_query_until_1_5_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{version}/all"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v > ApiVersion.V1_5_0)
)
def test_url_item_query_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    item: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{version}/{item}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(typ, agency, res, version, item, detail, refs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v > ApiVersion.V1_5_0)
)
def test_url_item_all_query_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{version}/*"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=refs
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V1_3_0)
)
def test_url_multiple_items_until_1_2_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    items: List[str],
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    q = StructureQuery(typ, agency, res, version, items, detail, refs)

    with pytest.raises(Invalid):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v > ApiVersion.V1_2_0 and v < ApiVersion.V2_0_0),
)
def test_url_multiple_items_until_1_5_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    items: List[str],
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{version}/{'+'.join(items)}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(typ, agency, res, version, items, detail, refs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v > ApiVersion.V1_5_0)
)
def test_url_multiple_items_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    items: List[str],
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{version}/{','.join(items)}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(typ, agency, res, version, items, detail, refs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v == ApiVersion.V1_1_0)
)
def test_url_hcl_before_1_2_0(
    hcl: StructureType,
    agency: str,
    res: str,
    version: str,
    item: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{hcl.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(hcl, agency, res, version, item, detail, refs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_2_0 and v < ApiVersion.V2_0_0
    ),
)
def test_url_hcl_since_1_2_0(
    hcl: StructureType,
    agency: str,
    res: str,
    version: str,
    item: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/{hcl.value}/{agency}/{res}/{version}/{item}"
        f"?detail={detail.value}&references={refs.value}"
    )

    q = StructureQuery(hcl, agency, res, version, item, detail, refs)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
def test_url_omit_default_item_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    item = "*"
    expected = f"/{typ.value}/{agency}/{res}/{version}"

    q = StructureQuery(typ, agency, res, version, item, detail, refs)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_omit_default_item_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    detail: StructureDetail,
    refs: StructureReference,
    api_version: ApiVersion,
):
    item = "*"
    expected = f"/structure/{typ.value}/{agency}/{res}/{version}"

    q = StructureQuery(typ, agency, res, version, item, detail, refs)
    url = q.get_url(api_version, True)

    assert url == expected
