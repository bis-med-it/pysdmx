import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import Dataflow


def check_dataflows(
    mock, fmr: RegistryClient, query, body, is_fusion: bool = False
):
    """get_dataflows() should return a collection of dataflows."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    flows = fmr.get_dataflows()

    assert len(mock.calls) == 1
    if is_fusion:
        assert (
            mock.calls[0].request.headers["Accept"] == Format.FUSION_JSON.value
        )
    else:
        assert (
            mock.calls[0].request.headers["Accept"]
            == Format.STRUCTURE_SDMX_JSON_2_0_0.value
        )

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
