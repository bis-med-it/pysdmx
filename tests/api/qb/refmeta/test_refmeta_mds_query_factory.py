import pytest

from pysdmx.api.qb.refmeta import RefMetaByMetadatasetQuery
from pysdmx.errors import Invalid
from pysdmx.model import Reference


@pytest.fixture
def ref() -> Reference:
    return Reference("MetadataSet", "BIS", "DTI_CBS", "2.1")


@pytest.fixture
def unsuported_ref() -> Reference:
    return Reference("Codelist", "SDMX", "CL_FREQ", "2.1")


def test_ref(ref: Reference):
    q = RefMetaByMetadatasetQuery.from_ref(ref)

    assert isinstance(q, RefMetaByMetadatasetQuery)
    assert q.provider_id == "BIS"
    assert q.metadataset_id == "DTI_CBS"
    assert q.version == "2.1"


def test_unknown_maintainable_ref(unsuported_ref: Reference):
    with pytest.raises(Invalid):
        RefMetaByMetadatasetQuery.from_ref(unsuported_ref)


__base_urn = "urn:sdmx:org.sdmx.infomodel."


def test_parse_urn():
    urn = f"{__base_urn}metadatastructure.MetadataSet=BIS:DTI_CBS(2.1)"

    q = RefMetaByMetadatasetQuery.from_ref(urn)

    assert isinstance(q, RefMetaByMetadatasetQuery)
    assert q.provider_id == "BIS"
    assert q.metadataset_id == "DTI_CBS"
    assert q.version == "2.1"


def test_parse_unsupported_urn():
    unsupported_urn = (
        f"{__base_urn}datastructure.DataStructure=ESTAT:CPI(2.1.0)"
    )

    with pytest.raises(Invalid):
        RefMetaByMetadatasetQuery.from_ref(unsupported_urn)
