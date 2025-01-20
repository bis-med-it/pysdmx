import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.model import Dataflow


def check_dataflows(mock, fmr: RegistryClient, query, body):
    """get_dataflows() should return a collection of dataflows."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    flows = fmr.get_dataflows()

    assert len(flows) == 5
    for df in flows:
        assert isinstance(df, Dataflow)
        assert df.id in [
            "TEST_ARRAYS_DF",
            "TEST_ARRAYS_DF_1",
            "TEST_ARRAYS_DF_2",
            "TEST_ARRAYS_DF_3",
            "TEST_FACETS_FLOW",
        ]
        assert df.agency == "TEST"
        assert df.name is not None
        assert df.version == "1.0"
        assert df.structure is not None


async def check_dataflows_async(mock, fmr: AsyncRegistryClient, query, body):
    """get_agencies() should return a collection of organizations."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    flows = await fmr.get_dataflows()

    assert len(flows) == 5
    for df in flows:
        assert isinstance(df, Dataflow)
        assert df.id in [
            "TEST_ARRAYS_DF",
            "TEST_ARRAYS_DF_1",
            "TEST_ARRAYS_DF_2",
            "TEST_ARRAYS_DF_3",
            "TEST_FACETS_FLOW",
        ]
        assert df.agency == "TEST"
        assert df.name is not None
        assert df.version == "1.0"
        assert df.structure is not None
