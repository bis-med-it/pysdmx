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

types_initial = [
    StructureType.DATA_STRUCTURE,
    StructureType.METADATA_STRUCTURE,
    StructureType.CATEGORY_SCHEME,
    StructureType.CONCEPT_SCHEME,
    StructureType.CODELIST,
    StructureType.HIERARCHICAL_CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.AGENCY_SCHEME,
    StructureType.DATA_PROVIDER_SCHEME,
    StructureType.DATA_CONSUMER_SCHEME,
    StructureType.ORGANISATION_UNIT_SCHEME,
    StructureType.DATAFLOW,
    StructureType.METADATAFLOW,
    StructureType.REPORTING_TAXONOMY,
    StructureType.PROVISION_AGREEMENT,
    StructureType.STRUCTURE_SET,
    StructureType.PROCESS,
    StructureType.CATEGORISATION,
    StructureType.CONTENT_CONSTRAINT,
    StructureType.ATTACHMENT_CONSTRAINT,
]

types_1_3_0 = [
    StructureType.ACTUAL_CONSTRAINT,
    StructureType.ALLOWED_CONSTRAINT,
]

types_1_5_0 = [
    StructureType.TRANSFORMATION_SCHEME,
    StructureType.RULESET_SCHEME,
    StructureType.USER_DEFINED_OPERATOR_SCHEME,
    StructureType.CUSTOM_TYPE_SCHEME,
    StructureType.NAME_PERSONALISATION_SCHEME,
    StructureType.NAME_ALIAS_SCHEME,
]

types_2_0_0_deprecated = [
    StructureType.HIERARCHICAL_CODELIST,
    StructureType.ORGANISATION_SCHEME,
    StructureType.STRUCTURE_SET,
    StructureType.CONTENT_CONSTRAINT,
    StructureType.ATTACHMENT_CONSTRAINT,
    StructureType.ACTUAL_CONSTRAINT,
    StructureType.ALLOWED_CONSTRAINT,
    StructureType.NAME_ALIAS_SCHEME,
]

types_2_0_0_added = [
    StructureType.DATA_CONSTRAINT,
    StructureType.METADATA_CONSTRAINT,
    StructureType.HIERARCHY,
    StructureType.HIERARCHY_ASSOCIATION,
    StructureType.VTL_MAPPING_SCHEME,
    StructureType.VALUE_LIST,
    StructureType.STRUCTURE_MAP,
    StructureType.REPRESENTATION_MAP,
    StructureType.CONCEPT_SCHEME_MAP,
    StructureType.CATEGORY_SCHEME_MAP,
    StructureType.ORGANISATION_SCHEME_MAP,
    StructureType.REPORTING_TAXONOMY_MAP,
    StructureType.METADATA_PROVIDER_SCHEME,
    StructureType.METADATA_PROVISION_AGREEMENT,
]

types_2_0_0_all = types_initial.copy()
types_2_0_0_all.extend(types_1_3_0)
types_2_0_0_all.extend(types_1_5_0)
types_2_0_0_all = [
    t for t in types_2_0_0_all if t not in types_2_0_0_deprecated
]
types_2_0_0_all.extend(types_2_0_0_added)


@pytest.fixture
def typ():
    return StructureType.CATEGORISATION


@pytest.fixture
def typs():
    return [StructureType.CATEGORISATION, StructureType.METADATAFLOW]


@pytest.fixture
def agency():
    return "SDMX"


@pytest.fixture
def res():
    return "CORE"


@pytest.fixture
def version():
    return "1.0"


@pytest.fixture
def detail():
    return StructureDetail.FULL


@pytest.fixture
def refs():
    return StructureReference.NONE


@pytest.mark.parametrize("api_version", ApiVersion)
def test_url_multiple_types_until_1_2_0(
    typs: List[StructureType], agency: str, res: str, api_version: ApiVersion
):
    with pytest.raises(ClientError):
        q = StructureQuery(typs, agency, res)
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
        f"/all/{agency}/{res}/{version}"
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
    with pytest.raises(ClientError):
        q = StructureQuery(
            atype, agency, res, version, detail=detail, references=refs
        )
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
    with pytest.raises(ClientError):
        q = StructureQuery(
            atype, agency, res, version, detail=detail, references=refs
        )
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
    with pytest.raises(ClientError):
        q = StructureQuery(
            atype, agency, res, version, detail=detail, references=refs
        )
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
    with pytest.raises(ClientError):
        q = StructureQuery(
            atype, agency, res, version, detail=detail, references=refs
        )
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
