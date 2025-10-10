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
