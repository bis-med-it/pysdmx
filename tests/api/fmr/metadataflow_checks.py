import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Metadataflow


def check_metadataflows(mock, fmr: RegistryClient, query, body):
    """get_metadataflows() returns a collection of metadataflows."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mdfs = fmr.get_metadataflows()

    __check_metadataflows(mdfs)


async def check_metadataflows_async(
    mock, fmr: AsyncRegistryClient, query, body
):
    """get_metadataflows() returns a collection of metadataflows (async)."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mdfs = await fmr.get_metadataflows()

    __check_metadataflows(mdfs)


def __check_metadataflows(mdfs):
    assert len(mdfs) == 1
    mdf = mdfs[0]
    assert isinstance(mdf, Metadataflow)
    assert mdf.id == "DF_CNF"
    assert mdf.agency == "TEST"
    assert mdf.name == "Dataflow Configuration Settings"
    assert mdf.version == "1.0"
    assert "MetadataStructure=TEST:DF_CNF(1.0)" in mdf.structure
    assert len(mdf.targets) == 1
    assert "Dataflow=*:*(*)" in mdf.targets[0]
