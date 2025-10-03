import httpx

from pysdmx.api.fmr import AsyncRegistryClient, RegistryClient
from pysdmx.io.format import Format
from pysdmx.model import MetadataProvisionAgreement


def check_metadata_provision_agreements(
    mock, fmr: RegistryClient, query, body, is_fusion: bool = False
):
    """get_metadata_provision_agreement() should return a mpa."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mpa = fmr.get_metadata_provision_agreement(
        "TEST", "DF_CNF_SDMX_TEST", "1.0"
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
    __check_mpa(mpa)


async def check_metadata_provision_agreements_async(
    mock, fmr: AsyncRegistryClient, query, body
):
    """get_metadata_provision_agreement() should return a mpa (async)."""
    mock.get(query).mock(
        return_value=httpx.Response(
            200,
            content=body,
        )
    )

    mpa = await fmr.get_metadata_provision_agreement(
        "TEST", "DF_CNF_SDMX_TEST", "1.0"
    )

    __check_mpa(mpa)


def __check_mpa(mpa):
    assert isinstance(mpa, MetadataProvisionAgreement)
    assert mpa.id == "DF_CNF_SDMX_TEST"
    assert mpa.name == "PAs for Dataflow Processing settings"
    assert mpa.agency == "TEST"
    assert mpa.description is None
    assert mpa.version == "1.0"
    assert "Metadataflow=TEST:DF_CNF(1.0)" in mpa.metadataflow
    assert (
        "MetadataProvider=SDMX:METADATA_PROVIDERS(1.0).TEST"
        in mpa.metadata_provider
    )
