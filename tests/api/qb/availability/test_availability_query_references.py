from typing import Sequence

import pytest

from pysdmx.api.qb.availability import AvailabilityQuery
from pysdmx.api.qb.structure import StructureReference
from pysdmx.api.qb.util import ApiVersion
from pysdmx.errors import ClientError

allowed_refs_v1 = [
    StructureReference.ALL,
    StructureReference.NONE,
    StructureReference.CODELIST,
    StructureReference.CONCEPT_SCHEME,
    StructureReference.DATAFLOW,
    StructureReference.DATA_PROVIDER_SCHEME,
    StructureReference.DATA_STRUCTURE,
]

allowed_refs_v2 = [
    StructureReference.ALL,
    StructureReference.NONE,
    StructureReference.CODELIST,
    StructureReference.CONCEPT_SCHEME,
    StructureReference.DATAFLOW,
    StructureReference.DATA_PROVIDER_SCHEME,
    StructureReference.DATA_STRUCTURE,
    StructureReference.VALUE_LIST,
]


@pytest.fixture()
def res():
    return "CBS"


@pytest.fixture()
def references():
    return StructureReference.ALL


@pytest.fixture()
def multiple_references():
    return [StructureReference.CODELIST, StructureReference.DATAFLOW]


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_invalid_value(res: str, api_version: ApiVersion):
    q = AvailabilityQuery(resource_id=res, references=42)

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
@pytest.mark.parametrize(
    "ref",
    (r for r in StructureReference if r not in allowed_refs_v1),
)
def test_invalid_ref_v1(
    res: str, ref: StructureReference, api_version: ApiVersion
):
    q = AvailabilityQuery(resource_id=res, references=ref)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version",
    (v for v in ApiVersion if v >= ApiVersion.V2_0_0),
)
@pytest.mark.parametrize(
    "ref",
    (r for r in StructureReference if r not in allowed_refs_v2),
)
def test_invalid_ref_v2(
    res: str, ref: StructureReference, api_version: ApiVersion
):
    q = AvailabilityQuery(resource_id=res, references=ref)

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
@pytest.mark.parametrize(
    "ref",
    (r for r in StructureReference if r in allowed_refs_v1),
)
def test_url_single_ref_before_2_0_0(
    res: str,
    ref: StructureReference,
    api_version: ApiVersion,
):
    expected = (
        f"/availableconstraint/all,{res},latest/all/all"
        "?references={ref.value}&mode=exact"
    )

    q = AvailabilityQuery(resource_id=res, references=ref)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize(
    "ref",
    (r for r in StructureReference if r in allowed_refs_v2),
)
def test_url_single_ref_since_2_0_0(
    ref: StructureReference,
    api_version: ApiVersion,
):
    expected = f"/availability/*/*/*/*/*/*?references={ref.value}&mode=exact"

    q = AvailabilityQuery(references=ref)
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
def test_url_multi_refs_before_2_0_0(
    res: str,
    multiple_references: Sequence[StructureReference],
    api_version: ApiVersion,
):
    q = AvailabilityQuery(resource_id=res, references=multiple_references)

    with pytest.raises(ClientError):
        q.get_url(api_version)


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multi_refs_since_2_0_0(
    multiple_references: Sequence[StructureReference],
    api_version: ApiVersion,
):
    refs = [r.value for r in multiple_references]
    expected = (
        f"/availability/*/*/*/*/*/*?references={','.join(refs)}&mode=exact"
    )

    q = AvailabilityQuery(references=multiple_references)
    url = q.get_url(api_version)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_multi_refs_since_2_0_0_short(
    multiple_references: Sequence[StructureReference],
    api_version: ApiVersion,
):
    refs = [r.value for r in multiple_references]
    expected = f"/availability?references={','.join(refs)}"

    q = AvailabilityQuery(references=multiple_references)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
@pytest.mark.parametrize(
    "ref",
    (
        r
        for r in StructureReference
        if r in allowed_refs_v1 and r != StructureReference.NONE
    ),
)
def test_url_single_ref_before_2_0_0_short(
    res: str,
    ref: StructureReference,
    api_version: ApiVersion,
):
    expected = f"/availableconstraint/{res}?references={ref.value}"

    q = AvailabilityQuery(resource_id=res, references=ref)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
@pytest.mark.parametrize(
    "ref",
    (
        r
        for r in StructureReference
        if r in allowed_refs_v2 and r != StructureReference.NONE
    ),
)
def test_url_single_ref_since_2_0_0_short(
    ref: StructureReference, api_version: ApiVersion
):
    expected = f"/availability?references={ref.value}"

    q = AvailabilityQuery(references=ref)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version",
    (
        v
        for v in ApiVersion
        if v >= ApiVersion.V1_3_0 and v < ApiVersion.V2_0_0
    ),
)
def test_url_default_ref_before_2_0_0_short(
    res: str,
    api_version: ApiVersion,
):
    references = StructureReference.NONE
    expected = f"/availableconstraint/{res}"

    q = AvailabilityQuery(resource_id=res, references=references)
    url = q.get_url(api_version, True)

    assert url == expected


@pytest.mark.parametrize(
    "api_version", (v for v in ApiVersion if v >= ApiVersion.V2_0_0)
)
def test_url_default_ref_since_2_0_0_short(api_version: ApiVersion):
    references = StructureReference.NONE
    expected = "/availability"

    q = AvailabilityQuery(references=references)
    url = q.get_url(api_version, True)

    assert url == expected
