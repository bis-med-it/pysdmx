import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import DataflowRef


def check_dfrefs(mock, fmr: RegistryClient, query, body):
    """get_agencies() should return a collection of organizations."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    refs = fmr.get_dataflows()

    assert len(refs) == 3
    for df in refs:
        assert isinstance(df, DataflowRef)
        assert df.id in ["CBS", "EXR", "ICP"]
        assert df.agency == "SDMX"
        assert df.name is not None
        if df.id == "CBS":
            assert df.description is not None
        else:
            assert df.description is None
        assert df.version == "1.0"


async def check_dfrefs_async(mock, fmr: AsyncRegistryClient, query, body):
    """get_agencies() should return a collection of organizations."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    refs = await fmr.get_dataflows()

    assert len(refs) == 3
    for df in refs:
        assert isinstance(df, DataflowRef)
