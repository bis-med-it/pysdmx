import pytest
from tests.api.qb.structure.test_common import (
    types_1_3_0,
    types_1_5_0,
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

refs_initial = [
    StructureReference.ALL,
    StructureReference.CHILDREN,
    StructureReference.DESCENDANTS,
    StructureReference.NONE,
    StructureReference.PARENTS,
    StructureReference.PARENTSANDSIBLINGS,
]

refs_2_0_0 = [StructureReference.ANCESTORS]


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


@pytest.fixture
def detail():
    return StructureDetail.FULL


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("references", refs_initial)
def test_url_core_refs_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    references: StructureReference,
    detail: StructureDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={references.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=references
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("references", refs_initial)
def test_url_core_refs_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    references: StructureReference,
    detail: StructureDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={references.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=references
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("references", refs_2_0_0)
def test_url_2_0_0_refs_since_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    references: StructureReference,
    detail: StructureDetail,
    api_version: ApiVersion,
):
    expected = (
        f"/structure/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={references.value}"
    )

    q = StructureQuery(
        typ, agency, res, version, detail=detail, references=references
    )
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("references", refs_2_0_0)
def test_url_2_0_0_refs_before_2_0_0(
    typ: StructureType,
    agency: str,
    res: str,
    version: str,
    references: StructureReference,
    detail: StructureDetail,
    api_version: ApiVersion,
):
    with pytest.raises(ClientError):
        q = StructureQuery(
            typ, agency, res, version, detail=detail, references=references
        )
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v < ApiVersion.V2_0_0)
)
@pytest.mark.parametrize("reference", types_initial)
def test_url_initial_type_before_2_0_0(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    reference: StructureType,
    api_version: ApiVersion,
):
    exp1 = (
        f"/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={reference.value}"
    )
    exp2 = (
        f"/{typ.value}/{agency}/{res}/{version}/all"
        f"?detail={detail.value}&references={reference.value}"
    )
    expected = [exp1, exp2]
    q = StructureQuery(
        typ,
        agency,
        res,
        version,
        detail=detail,
        references=StructureReference(reference.value),
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
@pytest.mark.parametrize("reference", types_1_3_0)
def test_url_v1_3_0_type_before_2_0_0(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    reference: StructureType,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={reference.value}"
    )
    q = StructureQuery(
        typ,
        agency,
        res,
        version,
        detail=detail,
        references=StructureReference(reference.value),
    )
    url = q.get_url(api_version)

    assert url in expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v == ApiVersion.V1_5_0),
)
@pytest.mark.parametrize("references", types_1_5_0)
def test_url_v1_5_0_type_before_2_0_0(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    references: StructureType,
    api_version: ApiVersion,
):
    expected = (
        f"/{typ.value}/{agency}/{res}/{version}"
        f"?detail={detail.value}&references={references.value}"
    )
    q = StructureQuery(
        typ,
        agency,
        res,
        version,
        detail=detail,
        references=StructureReference(references.value),
    )
    url = q.get_url(api_version)

    assert url in expected


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V1_3_0),
)
@pytest.mark.parametrize("reference", types_1_3_0)
def test_url_v1_3_0_type_before_1_3_0(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    reference: StructureType,
    api_version: ApiVersion,
):
    with pytest.raises(ClientError):
        q = StructureQuery(
            typ,
            agency,
            res,
            version,
            detail=detail,
            references=StructureReference(reference.value),
        )
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v < ApiVersion.V1_5_0),
)
@pytest.mark.parametrize("reference", types_1_5_0)
def test_url_v1_5_0_type_before_1_5_0(
    typ: StructureType,
    agency: str,
    version,
    res: str,
    detail: StructureDetail,
    reference: StructureType,
    api_version: ApiVersion,
):
    with pytest.raises(ClientError):
        q = StructureQuery(
            typ,
            agency,
            res,
            version,
            detail=detail,
            references=StructureReference(reference.value),
        )
        q.get_url(api_version)
