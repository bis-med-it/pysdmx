from typing import Sequence

import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import (
    Concept,
    DataType,
    MetadataComponent,
    MetadataStructure,
)


def check_msds(mock, fmr: RegistryClient, query, body):
    """get_metadata_structures() should return a collection of MSDs."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    msds = fmr.get_metadata_structures()

    assert len(mock.calls) == 1
    __check_msds(msds)


async def check_msds_async(mock, fmr: AsyncRegistryClient, query, body):
    """get_metadata_structures() should return a collection of MSDs (async)."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    msds = await fmr.get_metadata_structures()

    assert len(mock.calls) == 1
    __check_msds(msds)


def check_bug437(mock, fmr: RegistryClient, query, body):
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    msds = fmr.get_metadata_structures("ESTAT", "ACQUIS_COMPLIANCE_MSD", "1.2")

    assert len(mock.calls) == 1
    assert len(msds) == 1
    msd = msds[0]
    assert isinstance(msd, MetadataStructure)
    assert len(msd) == 19
    assert len(msd.components) == 4
    for c in msd.components:
        assert c.id in [
            "CONTACT",
            "SELFASSESSMENT_CTRY",
            "EVALUATION_ESTAT",
            "COMMENT_DSET",
        ]
        assert c.is_presentational is False
        assert c.concept is not None
        assert c.dtype == DataType.STRING
        assert c.facets is None
        assert c.enum_ref is None
        assert c.array_def is not None
        assert c.array_def.min_size == 0
        assert c.array_def.max_size is None
        if c.id == "CONTACT":
            assert len(c.components) == 5
            for cc in c.components:
                assert cc.id in [
                    "CONTACT_ORGANISATION",
                    "ORGANISATION_UNIT",
                    "CONTACT_NAME",
                    "CONTACT_EMAIL",
                    "CONTACT_PHONE",
                ]
                assert c.is_presentational is False
                assert c.concept is not None
                assert c.dtype == DataType.STRING
                assert c.facets is None
                assert c.enum_ref is None
                assert c.array_def is not None
                assert c.array_def.min_size == 0
                assert c.array_def.max_size is None
        elif c.id == "SELFASSESSMENT_CTRY":
            assert len(c.components) == 5
            for cc in c.components:
                assert cc.id in [
                    "ASSESSMENT",
                    "ASSESSMENT_COMPLIANCE",
                    "ACTION_FORESEEN",
                    "ASSISTANCE_REQ_CTRY",
                    "ASSISTANCE_COMMENT_CTRY",
                ]
                assert c.is_presentational is False
                assert c.concept is not None
                assert c.dtype == DataType.STRING
                assert c.facets is None
                assert c.enum_ref is None
                assert c.array_def is not None
                assert c.array_def.min_size == 0
                assert c.array_def.max_size is None
        elif c.id == "EVALUATION_ESTAT":
            assert len(c.components) == 5
            for cc in c.components:
                assert cc.id in [
                    "EVALUATION",
                    "EVALUATION_COMPLIANCE",
                    "ACTION_RECOMMENDED",
                    "ASSISTANCE_REQ_ESTAT",
                    "ASSISTANCE_COMMENT_ESTAT",
                ]
                assert c.is_presentational is False
                assert c.concept is not None
                assert c.dtype == DataType.STRING
                assert c.facets is None
                assert c.enum_ref is None
                assert c.array_def is not None
                assert c.array_def.min_size == 0
                assert c.array_def.max_size is None
        else:
            assert len(c.components) == 0


def __check_msds(msds: Sequence[MetadataStructure]):
    assert len(msds) == 1
    for msd in msds:
        assert isinstance(msd, MetadataStructure)
        assert msd.id == "SDG_MSD"
        assert msd.agency == "IAEG-SDGs"
        assert msd.name == "SDG Metadata Structure Definition"
        assert msd.version == "1.0"
        assert msd.description == (
            "Metadata Structure Definition for Sustainable "
            "Development Goals Indicators."
        )
        assert len(msd.components) == 44
        for cmp in msd.components:
            assert isinstance(cmp, MetadataComponent)
            assert cmp.is_presentational is False

            assert len(cmp.components) == 0
            assert isinstance(cmp.concept, Concept)
            assert cmp.facets is None
            assert cmp.enumeration is None
            if cmp.id == "META_LAST_UPDATE":
                assert cmp.dtype == DataType.DATE
            else:
                assert cmp.dtype == DataType.STRING
            if cmp.id == "COMPILING_ORG":
                assert cmp.array_def is not None
                assert cmp.array_def.min_size == 0
                assert cmp.array_def.max_size == 42
            elif cmp.id == "CONTACT":
                assert cmp.array_def is not None
                assert cmp.array_def.min_size == 1
                assert cmp.array_def.max_size is None
            else:
                assert cmp.array_def is None
            if cmp.id == "COLL_METHOD":
                assert cmp.enum_ref == (
                    "urn:sdmx:org.sdmx.infomodel.codelist.Codelist="
                    "BIS.MEDIT:MEDAL_INM(1.0)"
                )
            else:
                assert cmp.enum_ref is None
