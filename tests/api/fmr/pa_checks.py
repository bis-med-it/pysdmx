import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import ProvisionAgreement


def check_provision_agreements(
    mock, fmr: RegistryClient, query, body, is_fusion: bool = False
):
    """get_provision_agreement() should return a provision agreement."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    cat = fmr.get_provision_agreement("BIS.CBS", "CBS_BIS_5B0", "1.0")

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

    assert isinstance(cat, ProvisionAgreement)
    assert cat.id == "CBS_BIS_5B0"
    assert cat.name == "BIS for Consolidated Banking Statistics"
    assert cat.agency == "BIS.CBS"
    assert cat.description is None
    assert cat.version == "1.0"
    assert "Dataflow=BIS.CBS:CBS(1.0" in cat.dataflow
    assert "DataProvider=BIS:DATA_PROVIDERS(1.0).5B0" in cat.provider


async def check_provision_agreements_async(
    mock, fmr: AsyncRegistryClient, query, body
):
    """get_provision_agreement() should return a provision agreement."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    cat = await fmr.get_provision_agreement("BIS.CBS", "CBS_BIS_5B0", "1.0")

    assert isinstance(cat, ProvisionAgreement)
    assert cat.id == "CBS_BIS_5B0"
    assert cat.name == "BIS for Consolidated Banking Statistics"
    assert cat.agency == "BIS.CBS"
    assert cat.description is None
    assert cat.version == "1.0"
    assert "Dataflow=BIS.CBS:CBS(1.0" in cat.dataflow
    assert "DataProvider=BIS:DATA_PROVIDERS(1.0).5B0" in cat.provider
