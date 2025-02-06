import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import Categorisation


def check_categorisations(
    mock, fmr: RegistryClient, query, body, is_fusion: bool = False
):
    """get_categorisation() should return a catgeorisation."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    cat = fmr.get_categorisation(
        "TEST", "06E00965-AB55-F0C3-5CA3-9D454F3BE88F", "1.0"
    )

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

    assert isinstance(cat, Categorisation)
    assert cat.id == "06E00965-AB55-F0C3-5CA3-9D454F3BE88F"
    assert cat.name == (
        "Category 'TEST:TEST_CS(1.0).TWO.TWO_KID' linking "
        "to Dataflow 'TEST:TEST_FACETS_FLOW(1.0)'"
    )
    assert cat.agency == "TEST"
    assert cat.description is None
    assert cat.version == "1.0"
    assert "Dataflow=TEST:TEST_FACETS_FLOW(1.0)" in cat.source
    assert "Category=TEST:TEST_CS(1.0).TWO.TWO_KID" in cat.target


async def check_categorisations_async(
    mock, fmr: AsyncRegistryClient, query, body
):
    """get_categorisation() should return a catgeorisation."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    cat = await fmr.get_categorisation(
        "TEST", "06E00965-AB55-F0C3-5CA3-9D454F3BE88F", "1.0"
    )

    assert isinstance(cat, Categorisation)
    assert cat.id == "06E00965-AB55-F0C3-5CA3-9D454F3BE88F"
    assert cat.name == (
        "Category 'TEST:TEST_CS(1.0).TWO.TWO_KID' linking "
        "to Dataflow 'TEST:TEST_FACETS_FLOW(1.0)'"
    )
    assert cat.agency == "TEST"
    assert cat.description is None
    assert cat.version == "1.0"
    assert "Dataflow=TEST:TEST_FACETS_FLOW(1.0)" in cat.source
    assert "Category=TEST:TEST_CS(1.0).TWO.TWO_KID" in cat.target
